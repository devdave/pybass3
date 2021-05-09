import ctypes
import platform
import pathlib
from collections import defaultdict

from .datatypes import HANDLE

HERE = pathlib.Path(__file__).parent
TAG_FILE = HERE / "vendor" / "tags"


if platform.system().lower() == "windows":
    tags_module = ctypes.WinDLL(TAG_FILE.as_posix())
    func_type = ctypes.WINFUNCTYPE
else:
    raise NotImplementedError("Linux support isn't available")
    tags_module = ctypes.CDLL("./tags.so")
    func_type = ctypes.CFUNCTYPE

TAG_VERSION = 18

TAGS_GetLastErrorDesc = func_type(ctypes.c_char_p)(('TAGS_GetLastErrorDesc', tags_module))
TAGS_Read = func_type(ctypes.c_char_p,
                      ctypes.c_ulong, ctypes.c_char_p)(('TAGS_Read', tags_module))
TAGS_GetVersion = func_type(ctypes.c_ulong)(('TAGS_GetVersion', tags_module))


class BassTags:

    @classmethod
    def GetTags(cls, handle: HANDLE, format: str):
        return TAGS_Read(handle, format)

    @classmethod
    def GetDefaultTags(cls, handle):
        """
            See vendor/tags-readme.txt for what the various codes in the fmt
            string do.

        :param handle:
        :return:
        """
        divider = b"|//||"
        result = defaultdict(lambda : None)
        fmt_list = [
            b'track=%IFV1(%ITRM(%TRCK),%ITRM(%TRCK))',
            b'artist=%IFV1(%ITRM(%ARTI),%ICAP(%ITRM(%ARTI)))',
            b'title=%IFV1(%ITRM(%TITL),%ICAP(%ITRM(%TITL)))',
            b'album=%IFV1(%ITRM(%ALBM),%IUPC(%ITRM(%ALBM)))',
            b'year=%IFV1(%YEAR, %YEAR)',
            b'genre=%IFV1(%ITRM(%GNRE),%ITRM(%GNRE))',
            b'comment=%IFV1(%ITRM(%CMNT),[%ITRM(%CMNT)])'
        ]
        fmt_str = divider.join(fmt_list)
        retval = cls.GetTags(handle, fmt_str)
        if retval and len(retval) > 0:
            for element in retval.split(divider):
                name, value = element.split(b"=", 1) # type: (bytes, bytes,)
                name = name.decode("utf-8").strip()
                value = value.decode("utf-8",errors="ignore").strip() if len(value) > 0 else None
                result[name] = value

        return result





    @classmethod
    def GetVersion(cls):
        return TAGS_GetVersion()

    @classmethod
    def GetLastErrorDesc(cls):
        return TAGS_GetLastErrorDesc()
