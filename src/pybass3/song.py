from pathlib import Path
import typing as T
from uuid import uuid4
from hashlib import sha1
import logging
from collections import defaultdict

from .datatypes import HANDLE
from .bass_module import Bass
from .bass_channel import BassChannel
from .bass_stream import BassStream
from .bass_tags import BassTags

log = logging.getLogger(__name__)



class Song:

    _handle: HANDLE
    _length_seconds: float # Seconds
    _length_bytes: float

    _position_seconds: float # Seconds
    file_path: Path
    tags: dict
    _tags_fetched = False

    def __init__(self, file_path: T.Union[str, Path], length_seconds = None, length_bytes = None, tags = None):
        Bass.Init() # TODO is it appropriate to kick off BASS library initialization here?
        self.file_path = Path(file_path)
        # self._id = uuid4().hex
        self._id = sha1(str(self.file_path.as_posix()).encode("utf-8")).hexdigest()
        if self.file_path.exists() is False:
            raise ValueError(f"{file_path} doesn't exist")

        if self.file_path.is_file() is False:
            raise ValueError(f"{file_path=} is not a valid file")

        if tags is None:
            tags = {}


        self._handle = None
        self._length_seconds = length_seconds # Length in seconds
        self._length_bytes = length_bytes
        self._position_seconds = 0 # Current position in the song, in seconds
        self.tags = defaultdict(lambda : None, **tags)

    def __del__(self):
        """
            Ensure that the BASS library file handle is freed.

        :return:
        """
        # self.free_stream()
        pass

    @property
    def id(self):
        return self._id

    def _create_stream(self):
        # TODO - linux/OSX support breaking
        self._handle = BassStream.CreateFile(False, self.file_path.as_posix().encode("Windows-1252"))
        if self._length_bytes is None:
            self._length_bytes = BassChannel.GetLengthBytes(self._handle)
            self._length_seconds = BassChannel.GetLengthSeconds(self._handle, self._length_bytes)

        if self._tags_fetched is False:
            self.tags = BassTags.GetDefaultTags(self._handle)
            self._tags_fetched = True

    def free_stream(self, direct_stop=False) -> None:
        """
        Stop this music file from playing and frees its file handle from the BASS library.

        Args:
            direct_stop:  Should I call the underlying BassChannel Stop method instead of indirectly

        raises:
            BassException - If there is an issue releasing the file handle (eg it never existed).

        Returns:

        """
        if self._handle is not None:

            if self.is_playing or self.is_paused:
                if direct_stop is True and self._handle is not None:
                    BassChannel.Stop(self._handle)
                else:
                    self.stop()

            retval = BassStream.Free(self._handle)
            if retval is not True:
                Bass.RaiseError()

        self._handle = None

    def touch(self, do_not_release=False):
        self._create_stream()
        self.free_stream()


    @property
    def position(self) -> float:
        return BassChannel.GetPositionSeconds(self.handle)


    @property
    def position_bytes(self) -> int:
        return BassChannel.GetPositionBytes(self.handle)

    @property
    def position_time(self):
        seconds = int(self.position % 60)
        minutes = int(self.position // 60)

        return f"{minutes:02}:{seconds:02}"

    @property
    def duration(self) -> float:
        if self._length_seconds is None:
            if self._handle is None:
                self._create_stream()
                self.free_stream()

        return self._length_seconds

    @property
    def duration_bytes(self) -> int:
        if self._length_bytes is None:
            if self._handle is None:
                self._create_stream()
                self.free_stream()
        return self._length_bytes

    @property
    def duration_time(self):
        seconds = int(self.duration % 60)
        minutes = int(self.duration // 60)
        return f"{minutes:02}:{seconds:02}"

    @property
    def remaining_seconds(self):
        return self.duration - self.position

    @property
    def remaining_bytes(self):
        return self.duration_bytes - self.position_bytes

    @property
    def remaining_time(self):
        seconds = int(self.remaining_seconds % 60)
        minutes = int(self.remaining_seconds // 60)
        return f"{minutes:02}:{seconds:02}"


    @property
    def handle(self) -> HANDLE:
        if self._handle is None:
            self._create_stream()

        return self._handle



    @handle.deleter
    def handle(self):
        self.free_stream()

    def __len__(self):
        return BassChannel.GetLengthBytes(self.handle)

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
        if retval is not True:
            Bass.RaiseError()

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

    def __repr__(self):
        return f"<Song {self.file_path=!r}>"

    def __str__(self):
        return f"<Song {self.file_path=!r}>"
