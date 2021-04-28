
import enum
from pathlib import Path
import random

from .song import Song

try:
    import PySide2
except ImportError
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

class Playlist:

    VALID_TYPES = ["mp3", "mp4", "ogg", "opus"]

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

        self.queue_position = None
        self.current_song = None
        self.upcoming_song = None
        self.fade_in = None
        self.song_cls = Song

    def add_song(self, song_path):
        song = self.song_cls(song_path)
        self.songs.append(song)

    def add_directory(self, dir_path: Path, recurse=True):
        files = (file for file in dir_path.iterdir() if file.is_file() and file.suffix)
        dirs = (fdir for fdir in dir_path.iterdir() if fdir.is_dir())

        for song_path in files:
            self.add_song(song_path)

        if recurse is True:
            for fdir in dirs:
                self.add_directory(fdir, recurse)

    def set_fade(self, seconds):
        self.fade_in = seconds

    def set_randomize(self):
        ids = list(range(0, len(self.songs)))
        random.shuffle(ids)
        self.queue = ids
        self.mode = PlaylistMode.random

    def set_sequential(self):
        self.queue = list(range0, len(self.songs))
        self.mode = PlaylistMode.sequential


    def loop_song(self):
        self.play_mode = PlaylistMode.loop_single

    def loop_queue(self):
        self.play_mode = PlaylistMode.loop_all

    @property
    def current(self) -> Song:
        return self.current_song

    @property
    def upcoming(self) -> :
        song_id = self.queue[self.queue_position + 1]
        return self.songs[song_id]

    @property
    def prior(self):
        queue_pos = self.queue_position - 1
        if queue_pos < 0:
            queue_pos = len(self.songs)

        song_pos = self.queue[queue_pos]

        return self.songs[song_pos]

    def play(self):
        current = self.current
        current.play()


    def stop(self):
        self.current.stop()


    def pause(self):
        return self.current.pause()


    def restart(self):
        return self.current.move2position_seconds(0)


    def next(self):

        self.current.stop()
        self.current.free_stream()
        self.current = self.upcoming_song
        if self.current is not None:
            self.current.play()


    def previous(self):
        prior = self.prior
        self.current.stop()
        self.current_song.free_stream()
        self.current_song = self.upcoming_song
        self.current_song.play()


    def tick(self):
        current_pos = self.current.position_bytes
        current_duration = self.current.duration_bytes
        remaining = current_duration - current_pos
        remaining_seconds = self.current.duration - self.current.position

        if self.play_mode == PlaylistMode.loop_single:
            if current_pos >= current_duration:
                self.current.move2position_seconds(0)

        elif self.fade_in is not None and remaining_seconds <= self.fade_in:
            next_song = self.upcoming_song
            if next_song is not None:
                next_song.play()










