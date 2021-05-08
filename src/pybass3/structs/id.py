import ctypes

class ID3v1(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 3),
        ("title", ctypes.c_char * 30),
        ("artist", ctypes.c_char * 30),
        ("album", ctypes.c_char * 30),
        ("year", ctypes.c_char * 4),
        ("comment", ctypes.c_char * 30),
        ("genre", ctypes.c_byte)
    ]
