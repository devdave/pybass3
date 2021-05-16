"""
    Bass Channel manages/controls individual streams (play, pause, stop) plus reports state information like
    position and duration.

"""
import ctypes

from .bass_module import func_type, bass_module
from .datatypes import HANDLE, QWORD
from .codes import channel
from .structs.id import ID3v1

BASS_ChannelPlay = func_type(
    ctypes.c_bool,
    HANDLE,
    ctypes.c_bool)(('BASS_ChannelPlay', bass_module))

BASS_ChannelStop = func_type(
    ctypes.c_bool,
    HANDLE)(('BASS_ChannelStop', bass_module))

BASS_ChannelPause = func_type(
    ctypes.c_bool,
    HANDLE)(('BASS_ChannelPause', bass_module))

BASS_ChannelIsActive = func_type(
    ctypes.c_ulong,
    ctypes.c_ulong)(('BASS_ChannelIsActive', bass_module))

BASS_ChannelGetPosition = func_type(QWORD,
                                    ctypes.c_ulong,
                                    ctypes.c_ulong)(('BASS_ChannelGetPosition', bass_module))

BASS_ChannelSetPosition = func_type(ctypes.c_bool,
                                    ctypes.c_ulong,
                                    QWORD,
                                    ctypes.c_ulong)(('BASS_ChannelSetPosition', bass_module))

BASS_ChannelBytes2Seconds = func_type(
    ctypes.c_double,
    ctypes.c_ulong, QWORD)(('BASS_ChannelBytes2Seconds', bass_module))

BASS_ChannelSeconds2Bytes = func_type(
    QWORD,
    ctypes.c_ulong,
    ctypes.c_double)(('BASS_ChannelSeconds2Bytes', bass_module))

BASS_ChannelGetLength = func_type(QWORD,
                                  ctypes.c_ulong,
                                  ctypes.c_ulong)(('BASS_ChannelGetLength', bass_module))

BASS_ChannelGetTagsID3v1 = func_type(
    ctypes.POINTER(ID3v1),
    HANDLE,
    ctypes.c_ulong)(("BASS_ChannelGetTags", bass_module))


class BassChannel:
    """
        Managed wrapper around the various BASS_Channel functions

    """
    @classmethod
    def Play(cls, stream_handle: HANDLE, restart: bool = False) -> bool:
        """
            Play the given stream or if directed `restart` at position 0

        Args:
            stream_handle: A valid Bass Stream handle
            restart: If True, restart the stream from the beginning

        Returns:

        """
        return BASS_ChannelPlay(stream_handle, restart)

    @classmethod
    def Stop(cls, stream_handle: HANDLE) -> bool:
        """
            Stop's the given stream from playing to the output device.

        :param stream_handle:
        :return:
        """
        return BASS_ChannelStop(stream_handle)

    @classmethod
    def Pause(cls, stream_handle: HANDLE) -> bool:
        """
            Acts as a toggle, pausing or resuming a stream

        Args:
            stream_handle: A valid Bass stream handle

        Returns:

        """
        status = cls.IsActive(stream_handle)
        if status == channel.ACTIVE_PAUSED:
            return cls.Play(stream_handle)
        else:
            return BASS_ChannelPause(stream_handle)

    @classmethod
    def Resume(cls, stream_handle: HANDLE) -> bool:
        return cls.Play(stream_handle)

    @classmethod
    def IsActive(cls, stream_handle: HANDLE):
        return BASS_ChannelIsActive(stream_handle)

    @classmethod
    def IsPlaying(cls, stream_handle: HANDLE):
        retval = cls.IsActive(stream_handle)
        return retval == channel.ACTIVE_PLAYING

    @classmethod
    def IsPaused(cls, stream_handle: HANDLE):
        retval = cls.IsActive(stream_handle)
        return retval == channel.ACTIVE_PAUSED

    @classmethod
    def IsStopped(cls, stream_handle: HANDLE):
        retval = cls.IsActive(stream_handle)
        return retval == channel.ACTIVE_STOPPED

    @classmethod
    def GetPositionBytes(cls, stream_handle: HANDLE):
        return BASS_ChannelGetPosition(stream_handle, channel.POS_BYTE)

    @classmethod
    def GetPositionSeconds(cls, stream_handle: HANDLE) -> int:
        stream_bytes = cls.GetPositionBytes(stream_handle)
        return BASS_ChannelBytes2Seconds(stream_handle, stream_bytes)

    @classmethod
    def SetPositionBySeconds(cls, handle: HANDLE, seconds: float):
        stream_bytes = BASS_ChannelSeconds2Bytes(handle, seconds)
        return BASS_ChannelSetPosition(handle, stream_bytes, channel.POS_BYTE)

    @classmethod
    def SetPositionByBytes(cls, handle: HANDLE, bytes: int):
        return BASS_ChannelSetPosition(handle, bytes, channel.POS_BYTE)


    @classmethod
    def GetLengthSeconds(cls, stream_handle, stream_bytes = None):
        if stream_bytes is None:
            stream_bytes = cls.GetLengthBytes(stream_handle)

        return BASS_ChannelBytes2Seconds(stream_handle, stream_bytes)

    @classmethod
    def GetLengthStr(cls, stream_handle):
        value = cls.GetLengthSeconds(stream_handle)
        seconds = int(value%60)
        minutes = int(value/60)
        return f"{minutes:02}:{seconds:02}"

    @classmethod
    def GetPositionStr(cls, stream_handle):
        value = cls.GetPositionSeconds(stream_handle)
        seconds = int(value%60)
        minutes = int(value/60)
        return f"{minutes:02}:{seconds:02}"


    @classmethod
    def GetLengthBytes(cls, stream_handle: HANDLE):
        return BASS_ChannelGetLength(stream_handle, channel.POS_BYTE)

    @classmethod
    def GetID3v1Tags(cls, stream_handle: HANDLE):
        return BASS_ChannelGetTagsID3v1(stream_handle, channel.TAG_ID3)
