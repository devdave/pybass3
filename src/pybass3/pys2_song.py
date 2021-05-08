from PySide2 import QtCore

from .song import Song
from .bass_module import Bass
from .bass_channel import BassChannel



class Pys2Song(QtCore.QObject, Song):
    position_updated = QtCore.Signal(int) # length in bytes
    song_finished = QtCore.Signal()

    timer: QtCore.QTimer

    def __init__(self, file_path, precision: int = 500):
        """

        :param file_path: A valid file path to a music file
        :param precision: how often, in milliseconds, to pulse/emit song position in seconds
        """
        QtCore.QObject.__init__(self)
        Song.__init__(self, file_path)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(precision)
        self.timer.timeout.connect(self.pulser)

    @QtCore.Slot(int)
    def pulser(self):

        self.position_updated.emit(self.position)

        if self.remaining_bytes == 0:
            self.stop()
            self.song_finished.emit()


    def __del__(self) -> None:
        """
        I vaguely remember that exceptions from __del__ can be problematic but I'd rather
         this entire thing crash and burn than create a growing memory leak.
        Returns: None
        """
        self.free_stream(direct_stop=True)

    def play(self):
        super(Pys2Song, self).play()
        self.timer.start()

    def pause(self):
        super(Pys2Song, self).pause()
        self.timer.stop()

    def stop(self):
        super(Pys2Song, self).stop()
        self.timer.stop()

    @property
    def title(self):
        """
            Return a semi-useful song title

        :return:
        """
        tag_title = self.tags['title']
        tag_artist = self.tags['artist']

        if None not in [tag_title, tag_artist]:
            return f"{tag_artist} - {tag_title}"

        song_title = ""
        if tag_title is None:
            song_title, _ = self.file_path.name.rsplit(".", 1)

        song_artist = ""
        if tag_artist is None:
            song_artist = self.file_path.parent.name

        return f"{song_artist} - {song_title}"