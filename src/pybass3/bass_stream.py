import ctypes

from .bass_module import bass_module, Bass
from .bass_module import func_type
from .datatypes import QWORD, HSTREAM, HANDLE

BASS_StreamCreateFile = func_type(
    HSTREAM,
    ctypes.c_bool,
    ctypes.c_void_p,
    QWORD,
    QWORD,
    ctypes.c_ulong)(('BASS_StreamCreateFile', bass_module))

BASS_StreamFree = func_type(
    ctypes.c_bool,
    HSTREAM)(('BASS_StreamFree', bass_module))

BASS_StreamGetFilePosition = func_type(
    QWORD,
    HSTREAM,
    ctypes.c_ulong)(('BASS_StreamGetFilePosition', bass_module))

DEBUG_BASS_STREAM = False
OPEN_HANDLE_COUNT = 0

class BassStream:

    @classmethod
    def CreateFile(cls, mem, file, offset=0, length=0, flags=0):
        """

        Args:
            mem: stream the file from memory.
            file: Filename (mem = FALSE) or a memory location (mem = TRUE).
            offset: File offset to begin streaming from (only used if mem = FALSE).
            length: Data length... 0 = use all data up to the end of the file (if mem = FALSE).
            flags:

        Returns:

        """
        global DEBUG_BASS_STREAM, OPEN_HANDLE_COUNT

        handle = BASS_StreamCreateFile(mem, file, offset, length, flags)

        if handle == 0:
            Bass.RaiseError(f"file={file!r}")

        if DEBUG_BASS_STREAM is True:
            OPEN_HANDLE_COUNT += 1

        return handle

    @classmethod
    def Free(cls, handle: HANDLE):
        """
            Free a stream handle.   Fails silently if there is an issue freeing
            the given handle

        :param handle: The BASS stream handle to free
        :return:
        """
        global DEBUG_BASS_STREAM, OPEN_HANDLE_COUNT
        retval = BASS_StreamFree(handle)
        if DEBUG_BASS_STREAM is True:
            OPEN_HANDLE_COUNT -= 1