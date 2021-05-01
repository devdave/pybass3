"""
    Pyside2 compatible Playlist object


"""
from PySide2 import QtCore

Qt = QtCore.Qt

from pys2_song import Pys2Song

from .playlist import Playlist


class Pys2Playlist(QtCore.QObject, Playlist):
    song_added = QtCore.Signal(int)  # Song ID, Qt DOES NOT like when I try to pass the Song object
    song_changed = QtCore.Signal(int)  # Song ID
    music_paused = QtCore.Signal(int)
    music_playing = QtCore.Signal(int)
    music_stopped = QtCore.Signal(int)

    def __init__(self):
        QtCore.QObject.__init__(self)
        Playlist.__init__(self, Pys2Song)

    def add_song(self, song_path):
        return super(Playlist, self).add_song(song_path)

    def play(self):
        super(QtPlaylist, self).play()
        if self.current.is_playing:
            self.music_playing.emit(self.song_id)

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

    def stop(self):
        super(Playlist, self).stop()
        if self.current.is_stopped:
            self.music_stopped.emit(self.song_id)

    def pause(self):
        super(Playlist, self).pause()
        if self.current.is_paused:
            self.music_paused.emit(self.song_id)










