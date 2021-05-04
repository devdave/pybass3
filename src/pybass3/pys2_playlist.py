"""
    Pyside2 compatible Playlist object


"""
import logging

from PySide2 import QtCore

Qt = QtCore.Qt

from .pys2_song import Pys2Song
from .playlist import Playlist, PlaylistMode

log = logging.getLogger(__name__)

class Pys2Playlist(QtCore.QObject, Playlist):
    song_added = QtCore.Signal(str)  # Song ID, Qt DOES NOT like when I try to pass the Song object
    songs_added = QtCore.Signal(list) # list of Song ID's
    song_changed = QtCore.Signal(str)  # Song ID
    music_paused = QtCore.Signal(str)
    music_playing = QtCore.Signal(str)
    music_stopped = QtCore.Signal(str)

    ticked = QtCore.Signal()

    def __init__(self, tick_precision = 500):
        QtCore.QObject.__init__(self)
        Playlist.__init__(self, Pys2Song)
        self.ticker = QtCore.QTimer()
        self.ticker.setInterval(tick_precision)

        self.ticker.timeout.connect(self.tick)

        log.debug("Initialized playlist: Precision is %s", tick_precision)



    def add_song(self, song_path):
        return super(Playlist, self).add_song(song_path)
        log.debug("Pys2Playlist.add_song %s", song_path)

    def play(self):
        super(QtPlaylist, self).play()
        if self.current.is_playing and self.current is not None:
        log.debug("Pys2Playlist.play self.current is %s", self.current)
            self.music_playing.emit(self.current.id)

    def play_song(self, song_id):
        log.debug("Pys2Playlist.play_song %s", song_id)

        if self.fadein_song is not None:
            self.fadein_song.free_stream()
            self.fadein_song = None

        if self.current is not None:
            self.current.free_stream()
            self.current = None

        self.current = self.songs[song_id]
        self.current.play()

        self.music_playing.emit(song_id)

    def stop(self):
        super(Playlist, self).stop()
        if self.current.is_stopped and self.current is not None:
        log.debug("Pys2Playlist.stop called")
            self.music_stopped.emit(self.current.id)

    def pause(self):
        super(Playlist, self).pause()
        if self.current.is_paused and self.current is not None:
        log.debug("Pys2Playlist.pause called")
            self.music_paused.emit(self.current.id)

        log.debug("Pys2Playlist.previous")



    def tick(self):

        if self.current is not None:
            remaining = self.current.remaining_bytes
            remaining_seconds = self.current.remaining_seconds
        else:
            log.debug("TICKER ACTIVE WITH NO SONG")
            self.ticker.stop()
            return

        if self.play_mode == PlaylistMode.loop_single and remaining <= 0:
            log.debug("TICK - Repeating %s", self.current.file_path)
            self.current.move2position_seconds(0)
            self.song_changed.emit(self.current.id)


        elif self.fade_in is not None and remaining_seconds <= self.fade_in:
            if self.fadein_song is not None and remaining <= 0:
                log.debug("TICK - Fade in progress switching to current")
                self.current.stop()
                self.current.free_stream()
                self.current = self.fadein_song
                self.fadein_song = None
                self.queue_position += 1
                self.song_changed.emit(self.current.id)

            elif self.fadein_song is None and self.upcoming is not None:
                log.debug("TICK - fading in song")
                self.fadein_song = self.upcoming
                self.fadein_song.play()

        elif remaining <= 0 and self.current is not None:
            log.debug("TICK - current is finished, moving to next song")
            self.current.stop()
            self.current.free_stream()
            self.current = self.next()
            if self.current is not None:
                self.queue_position += 1
                self.current.play()
                self.song_changed.emit(self.current.id)

        self.ticked.emit()






