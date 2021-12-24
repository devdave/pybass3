"""
    Pyside2 compatible Playlist object


"""
import logging
import pathlib

from PySide2 import QtCore

Qt = QtCore.Qt

from .pys2_song import Pys2Song
from .playlist import Playlist, PlaylistMode

log = logging.getLogger(__name__)

class PlaylistSignals(QtCore.QObject, Playlist):
    song_added = QtCore.Signal(str)  # Song ID, Qt DOES NOT like when I try to pass the Song object
    songs_added = QtCore.Signal(tuple)  # the starting index and a list of Song ID's
    song_changed = QtCore.Signal(str)  # Song ID
    song_updated = QtCore.Signal(int)  # Song by index/row #
    playlist_cleared = QtCore.Signal()

    music_paused = QtCore.Signal(str)
    music_playing = QtCore.Signal(str)
    music_stopped = QtCore.Signal(str)

    queue_changed = QtCore.Signal()
    ticked = QtCore.Signal()

class Pys2Playlist(QtCore.QObject, Playlist):
    """
    Extension to the Playlist class which fires QT5/Pyside2 signals
    for when songs are added (group or individual), when the song changes, as well as reports when
    the state (play, pause, stop) occurs.

    """

    signals: PlaylistSignals

    def __init__(self, tick_precision = 500, songs = None):
        QtCore.QObject.__init__(self)
        Playlist.__init__(self, Pys2Song, songs=songs)
        log.debug("QT Playlist initialzied")

        self.signals = PlaylistSignals()
        self.ticker = QtCore.QTimer()
        self.ticker.setInterval(tick_precision)

        self.ticker.timeout.connect(self.tick)

        log.debug("Initialized playlist: Precision is %s", tick_precision)

    def add_song(self, song_obj: Pys2Song, add2queue=True, supress_emit = False) -> Pys2Song:
        song = super(Pys2Playlist, self).add_song(song_obj, add2queue=add2queue)
        if supress_emit is False and song is not None:
            self.signals.song_added.emit(song.id)

        return song


    def add_song_by_path(self, song_path: pathlib.Path, add2queue=True, suppress_emit = False) -> Pys2Song:
        log.debug("Pys2Playlist.add_song %s", song_path)
        song = super(Pys2Playlist, self).add_song_by_path(song_path, add2queue=add2queue)
        if suppress_emit is False and song is not None:
            self.signals.song_added.emit(song.id)

        return song

    def add_directory(self, dir_path: pathlib.Path, recurse=True, top = False, suppress_emit = True):
        """

        :param dir_path: The directory to scan for music
        :param recurse: Should sub directories be walked over
        :param Top: Is this the top level method in the recursion
        :param suppress_emit: If True, don't Signal each song discovery
        :return: A list of song_ids
        """
        log.debug("Playlist.add_directory called with %s", dir_path)
        dir_path = pathlib.Path(dir_path) # Make sure I am dealing with pathlib
        files = (file for file in dir_path.iterdir() if file.is_file() and file.suffix in self.VALID_TYPES)
        dirs = (fdir for fdir in dir_path.iterdir() if fdir.is_dir())

        index_position = -1 if top is False else len(self)+1
        song_ids = []

        for song_path in files:
            try:
                song = self.add_song_by_path(song_path, suppress_emit=suppress_emit)
                if song is not None:
                    song_ids.append(song.id)
            except TypeError as exc:
                debug = 1
                pass


        if recurse is True:
            for fdir in dirs:
                _, sub_song_ids = self.add_directory(fdir, recurse, top=False, suppress_emit=suppress_emit)
                song_ids.extend(sub_song_ids)

        if top is True and suppress_emit is True:
            self.signals.songs_added.emit((index_position, song_ids))

        return index_position, song_ids



    def play(self):
        log.debug("Pys2Playlist.play self.current is %s", self.current)

        new_song = self.current is None

        super(Pys2Playlist, self).play()
        if self.current is not None and self.current.is_playing:
            self.signals.music_playing.emit(self.current.id)
            self.ticker.start()

        if new_song is True and self.current is not None:
            self.signals.song_changed.emit(self.current.id)

    def play_song_by_index(self, song_index) -> Pys2Song:
        log.debug("Playing by index %s", song_index)
        song = super(Pys2Playlist, self).play_song_by_index(song_index)

        self.signals.song_changed.emit(song.id)
        self.signals.music_playing.emit(song.id)

        return song

    def play_song_by_id(self, song_id) -> Pys2Song:
        log.debug("Playing by id %s", song_id)
        song = super(Pys2Playlist, self).play_song_by_id(song_id)
        if song is not None:
            self.signals.song_changed.emit(song.id)
            self.signals.music_playing.emit(song.id)

        return song


    def play_first(self) -> Pys2Song:
        log.debug("Playing first")
        song = super(Pys2Playlist, self).play_first()
        if song is not None:
            self.signals.song_changed.emit(song.id)
            self.signals.music_playing.emit(song.id)
        return song

    def stop(self):
        log.debug("Pys2Playlist.stop called")

        super(Pys2Playlist, self).stop()
        if self.current is not None:
            self.signals.music_stopped.emit(self.current.id)
            
        self.ticker.stop()

    def pause(self):
        log.debug("Pys2Playlist.pause called")
        super(Pys2Playlist, self).pause()
        if self.current is not None:
            self.signals.music_paused.emit(self.current.id)

        self.ticker.stop()
        
    def previous(self):
        log.debug("Pys2Playlist.previous")
        result = super(Pys2Playlist, self).previous()
        log.debug("Pys2Playlist.previous changed to %r", result)
        if result is not None:
            self.signals.song_changed.emit(result.id)
        
    def next(self):
        log.debug("Pys2Playlist.next")
        result = super(Pys2Playlist, self).next()
        log.debug("Next song is %r", result)
        if result is not None:
            self.signals.song_changed.emit(result.id)

        return result

    def clear(self):
        self.ticker.stop()
        super(Pys2Playlist, self).clear()
        self.signals.playlist_cleared.emit()

    def tick(self):

        if self.current is not None:
            remaining = self.current.remaining_bytes
            remaining_seconds = self.current.remaining_seconds
        else:
            log.error("TICKER ACTIVE WITH NO SONG")
            self.ticker.stop()
            return

        if self.play_mode == PlaylistMode.loop_single and remaining <= 0:
            log.debug("TICK - Repeating %s", self.current.file_path)
            self.current.move2position_seconds(0)
            self.signals.song_changed.emit(self.current.id)


        elif self.fade_in > 0 and remaining_seconds <= self.fade_in:
            if self.fadein_song is not None and (remaining <= 0 or remaining_seconds < 1):
                log.debug("TICK - Fade in progress switching to current")
                self.current.stop()
                self.current.free_stream()
                self.current = self.fadein_song
                self.fadein_song = None
                self.queue_position += 1
                self.signals.song_changed.emit(self.current.id)

            elif self.fadein_song is None and self.upcoming is not None:
                log.debug("TICK - fading in song")
                self.fadein_song = self.upcoming
                self.fadein_song.play()

        elif remaining <= 0 or remaining_seconds < 1:
            log.debug("TICK - current is finished, moving to next song")
            # self.current.stop()
            self.current.free_stream()
            self.current = self.next()
            if self.current is not None:
                self.queue_position += 1
                self.current.play()
                self.signals.song_changed.emit(self.current.id)
            else:
                log.debug("TICK - playlist has reached the end of the queue and is not looping")


        self.signals.ticked.emit()


    def set_sequential(self, restart_and_play = True):
        super(Pys2Playlist, self).set_sequential(restart_and_play=restart_and_play)
        self.signals.queue_changed.emit()

    def set_randomize(self, restart_and_play=True):
        super(Pys2Playlist, self).set_randomize(restart_and_play=restart_and_play)
        self.signals.queue_changed.emit()




