
import enum
from pathlib import Path
import random

from .bass_module import BassException
from .song import Song

try:
    import PySide2
    HAS_PYSIDE2 = True
except ImportError:
    HAS_PYSIDE2 = False


class PlaylistState(enum.Enum):
    stopped = enum.auto()
    playing = enum.auto()
    paused = enum.auto()
    error = enum.auto()


class PlaylistMode(enum.Enum):
    loop_single = enum.auto()
    loop_all = enum.auto()
    one_time = enum.auto()

    sequential = enum.auto()
    random = enum.auto()

    progress_on_error = enum.auto()
    die_on_error = enum.auto()

class Playlist:

    VALID_TYPES = [".mp3", ".mp4", ".ogg", ".opus"]

    songs:list # The songs the playlist knows about
    queue: list # The order songs will be played in
    state: PlaylistState # Is the playlist playing songs, stopped, or paused?
    mode: PlaylistMode # Is the playlist running sequential or random
    play_mode: PlaylistMode # is the playlist looping the whole queue, just a song, or running to end?

    queue_position: int  # Where is the playlist in the current queue
    current_song: Song # What is currently playing
    fadein_song: Song # if fade_in is not None, this is the next song to play
    fade_in: int # How soon should the next song start playing, None if lock step
    song_cls: Song # What is the container for a song (eg Song or QtSong)



    def __init__(self, song_cls = Song):
        self.songs = []
        self.queue = []
        self.state = PlaylistState.stopped
        self.mode = PlaylistMode.sequential
        self.play_mode = PlaylistMode.one_time

        self.error_mode = PlaylistMode.progress_on_error

        self.queue_position = None
        self.current_song = None

        self.fade_in = None
        self.fadein_song = None
        self.song_cls = song_cls

    @property
    def song_id(self):
        if self.queue_position is None:
            if self.mode == PlaylistMode.sequential:
                self.set_sequential()
            else:
                self.set_randomize()

            if self.queue_position is None:
                self.queue_position = 0

        return self.queue[self.queue_position]

    def add_song(self, song_path):
        song = self.song_cls(song_path)
        song.duration
        song.free_stream()
        self.songs.append(song)
        self.queue.append(len(self.songs)-1)
        return len(self.songs)-1, song

    def add_directory(self, dir_path: Path, recurse=True):
        files = (file for file in dir_path.iterdir() if file.is_file() and file.suffix in self.VALID_TYPES)
        dirs = (fdir for fdir in dir_path.iterdir() if fdir.is_dir())

        for song_path in files:
            self.add_song(song_path)

        if recurse is True:
            for fdir in dirs:
                self.add_directory(fdir, recurse)

    @property
    def fade(self):
        return self.fade_in

    @fade.setter
    def fade(self, value):
        self.fade_in = value

    @fade.deleter
    def fade(self):
        self.fade_in = None

    def set_randomize(self):
        ids = list(range(0, len(self.songs)))
        random.shuffle(ids)
        self.queue = ids
        self.mode = PlaylistMode.random

    def set_sequential(self):
        self.queue = list(range(0, len(self.songs)))
        self.mode = PlaylistMode.sequential

    def loop_song(self):
        self.play_mode = PlaylistMode.loop_single

    def loop_queue(self):
        self.play_mode = PlaylistMode.loop_all

    @property
    def current(self) -> Song:
        return self.current_song

    @current.setter
    def current(self, new_song):
        if self.current_song is not None:
            self.current_song.free_stream()
        self.current_song = new_song
        return self.current_song

    @current.deleter
    def current(self):
        if self.current_song is not None:
            self.current_song.free_stream()



    @property
    def upcoming(self) -> Song:
        qpos = self.queue_position + 1
        # Is the next song past the queue's length?
        if qpos >= len(self.queue):
            qpos = 0

        song_id = self.queue[self.queue_position + 1]

        return self.songs[song_id]

    @property
    def prior(self):
        qpos = self.queue_position - 1
        if qpos < 0:
            queue_pos = len(self.songs) - 1

        song_pos = self.queue[qpos]

        return self.songs[song_pos]

    def play(self):

        if self.fadein_song is not None:
            self.fadein_song.play()

        if self.current is None:
            if len(self.queue) == 0:
                if self.mode == PlaylistMode.sequential:
                    self.set_sequential()
                else:
                    self.set_randomize()

            self.queue_position = 0
            current_id = self.queue[self.queue_position]
            self.current_song = self.songs[current_id]
        self.current.play()


    def stop(self):
        if self.fadein_song is not None:
            self.fadein_song.stop()

        self.current.stop()


    def pause(self):
        if self.fadein_song is not None:
            self.fadein_song.pause()

        return self.current.pause()


    def restart(self):
        if self.fadein_song is not None:
            self.fadein_song.free_stream()
            self.fadein_song = None

        return self.current.move2position_seconds(0)


    def next(self):
        try:
            return self._next()
        except BassException as bexc:
            if self.error_mode == PlaylistMode.progress_on_error:
                self.queue_position += 1
                if self.queue_position > len(self.queue):
                    self.queue_position = 0

                return self._next()

    def _next(self):

        if self.fadein_song is not None:
            self.current.stop()
            self.current = self.fadein_song
            self.fadein_song = None

        else:
            self.current.free_stream()
            self.current = self.upcoming
            if self.current is not None:
                self.current.play()

        self.queue_position += 1
        if self.queue_position > len(self.queue):
            self.queue_position = 0

        song_id = self.queue[self.queue_position]
        return song_id, self.current

    def previous(self):
        try:
            return self._previous()
        except BaseException:
            if self.error_mode == PlaylistMode.progress_on_error:
                self.queue_position -= 1
                if self.queue_position < 0:
                    self.queue_position = len(self.queue)

                return self._previous()
            else:
                raise


    def _previous(self):
        prior = self.prior
        if self.fadein_song is not None:
            self.fadein_song.free_stream()
            self.fadein_song = None
            self.current.move2position_seconds(0)
            self.current.play()
        else:
            self.current_song.free_stream()
            self.current_song = prior
            self.current_song.play()

            self.queue_position -= 1
            if self.queue_position < 0:
                self.queue_position = len(self.queue)

        song_id = self.queue[self.queue_position]
        return song_id, self.current

    def tick(self):
        current_pos = self.current.position_bytes
        current_duration = self.current.duration_bytes
        remaining = current_duration - current_pos
        remaining_seconds = self.current.duration - self.current.position

        if self.play_mode == PlaylistMode.loop_single:
            if current_pos >= current_duration:
                self.current.move2position_seconds(0)

        elif self.fade_in is not None and remaining_seconds <= self.fade_in:
            if self.fadein_song is not None:
                if remaining <= 0:
                    self.current.stop()
                    self.current.free_stream()
                    self.current = self.fadein_song
                    self.fadein_song = None
                    self.queue_position += 1
            elif self.upcoming is not None:
                self.fadein_song = self.upcoming
                self.fadein_song.play()

        elif remaining <= 0:
            self.current.stop()
            self.current.free_stream()
            self.next()
            self.current.play()

    def items(self):
        for song_id, song in enumerate(self.songs):
            yield song_id, song

    def __len__(self):
        return len(self.songs)


if HAS_PYSIDE2:
    from PySide2 import QtCore
    from PySide2 import QtWidgets

    Qt = QtCore.Qt

    from .song import QtSong

    class QtPlaylist(QtCore.QObject, Playlist):

        song_added = QtCore.Signal(int) # Song ID, Qt DOES NOT like when I try to pass the Song object
        song_changed = QtCore.Signal(int)  # Song ID
        music_paused = QtCore.Signal(int)
        music_playing = QtCore.Signal(int)
        music_stopped = QtCore.Signal(int)

        timer: QtCore.QTimer

        def __init__(self):
            QtCore.QObject.__init__(self)
            Playlist.__init__(self, QtSong)

            self.timer = QtCore.QTimer()
            self.timer.setInterval(500)
            self.timer.timeout.connect(self.tick)

        def add_song(self, song_path):
            return super(QtPlaylist, self).add_song(song_path)

            # self.song_added.emit([index, song])

        def play(self):
            super(QtPlaylist, self).play()
            if self.current.is_playing:
                self.music_playing.emit(self.song_id)
                self.timer.start()

        def play_song(self, song_id):
            if self.fadein_song is not None:
                self.fadein_song.free_stream()
                self.fadein_song = None

            if self.current is not None:
                self.current.free_stream()
                self.current = None

            self.current = self.songs[song_id]
            self.current.play()

            self.music_playing.emit(song_id)
            self.timer.start()

        def stop(self):
            super(QtPlaylist, self).stop()
            if self.current.is_stopped:
                self.music_stopped.emit(self.song_id)

            self.timer.stop()

        def pause(self):
            super(QtPlaylist, self).pause()
            if self.current.is_paused:
                self.music_paused.emit(self.song_id)

            self.timer.stop()











