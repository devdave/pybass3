from pathlib import Path
import typing as T

try:
    from PySide2 import QtCore
    HAS_PYSIDE2 = True
except ImportError:
    HAS_PYSIDE2 = False

from .datatypes import HANDLE
from .bass_module import Bass
from .bass_channel import BassChannel
from .bass_stream import BassStream


class Song:

    _handle: HANDLE
    _handle_length: float
    _handle_position: float

    def __init__(self, file_path):
        super(Song, self).__init__()
        Bass.Init()
        self.file_path = Path(file_path)
        assert self.file_path.exists() and self.file_path.is_file(), f"{self.file_path} doesn't exist or is not a file"

        self._handle = None
        self._handle_length = None # Length in seconds
        self._handle_position = 0 # Current position in the song, in seconds

    def __del__(self):
        self.free_stream()

    def free_stream(self):
        if self._handle is not None:

            if self.is_playing or self.is_paused:
                self.stop()

            retval = BassStream.Free(self._handle)
            if retval is not True:
                Bass.RaiseError()

        self._handle = None

    @property
    def position(self):
        return BassChannel.GetPositionSeconds(self.handle)


    @property
    def position_bytes(self):
        return BassChannel.GetPositionBytes(self.handle)

    @property
    def duration(self):
        if self._handle is None:
            self._create_stream()

        return self._handle_length

    @property
    def duration_bytes(self):
        return BassChannel.GetLengthBytes(self.handle)

    @property
    def handle(self):
        if self._handle is None:
            self._create_stream()

        return self._handle

    def _create_stream(self):
        self._handle = BassStream.CreateFile(False, bytes(self.file_path))
        self._handle_length = BassChannel.GetLengthSeconds(self._handle, BassChannel.GetLengthBytes(self.handle))

    @handle.deleter
    def handle(self):
        self.free_stream()

    def __len__(self):
        length = BassChannel.GetLengthBytes(self.handle)

    @property
    def is_playing(self):
        return BassChannel.IsPlaying(self.handle)

    @property
    def is_paused(self):
        return BassChannel.IsPaused(self.handle)

    @property
    def is_stopped(self):
        return BassChannel.IsStopped(self.handle)

    def move2position_seconds(self, seconds: float):
        retval = BassChannel.SetPositionBySeconds(self.handle, seconds)
        if retval is not True:
            Bass.RaiseError()
        return retval

    def move2position_bytes(self, bytes: int):
        """
            Repositioning by bytes is drastically more precise and is the recommend
            method for seeking through a song.

        :param bytes:
        :return:
        """
        retval = BassChannel.SetPositionByBytes(self.handle, bytes)

    def play(self):
        retval = BassChannel.Play(self.handle, False)
        if retval is not True:
            Bass.RaiseError()

    def stop(self):
        retval = BassChannel.Stop(self.handle)
        if retval is not True:
            Bass.RaiseError()

    def pause(self):
        retval = BassChannel.Pause(self.handle)
        if retval is not True:
            Bass.RaiseError()

    def resume(self):
        retval = BassChannel.Pause(self.handle)
        if retval is not True:
            Bass.RaiseError()

    def __hash__(self):
        return hash(self.file_path)



if HAS_PYSIDE2:
    class QtSong(QtCore.QObject, Song):
        position_updated = QtCore.Signal(int)
        song_finished = QtCore.Signal()

        timer: QtCore.QTimer

        def __init__(self, file_path, precision: int=500):
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
            position = BassChannel.GetPositionSeconds(self.handle)
            self.position_updated.emit(position)

        def __del__(self) -> None:
            """
            I vaguely remember that exceptions from __del__ can be problematic but I'd rather
             this entire thing crash and burn than create a growing memory leak.
            Returns: None
            """
            self.free_stream()


        def play(self):
            super(QtSong, self).play()
            self.timer.start()

        def stop(self):
            super(QtSong, self).stop()
            self.timer.stop()


