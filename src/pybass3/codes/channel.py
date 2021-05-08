# BASS_ChannelIsActive return values
ACTIVE_STOPPED = 0
ACTIVE_PLAYING = 1
ACTIVE_STALLED = 2
ACTIVE_PAUSED = 3
ACTIVE_PAUSED_DEVICE = 4

# BASS_ChannelGetLength/GetPosition/SetPosition modes
POS_BYTE = 0  # byte position
POS_MUSIC_ORDER = 1  # order.row position, MAKELONG(order,row)
POS_OGG = 3  # OGG bitstream number
POS_RESET = 0x2000000  # flag: reset user file buffers
POS_RELATIVE = 0x4000000  # flag: seek relative to the current position
POS_INEXACT = 0x8000000  # flag: allow seeking to inexact position
POS_DECODE = 0x10000000  # flag: get the decoding (not playing) position
POS_DECODETO = 0x20000000  # flag: decode to the position instead of seeking
POS_SCAN = 0x40000000  # flag: scan to the position

# BASS_ChannelGetTags types : what's returned
TAG_ID3 = 0  # ID3v1 tags : TAG_ID3 structure
TAG_ID3V2 = 1  # ID3v2 tags : variable length block
TAG_OGG = 2  # OGG comments : series of null-terminated UTF-8 strings
TAG_HTTP = 3  # HTTP headers : series of null-terminated ANSI strings
TAG_ICY = 4  # ICY headers : series of null-terminated ANSI strings
TAG_META = 5  # ICY metadata : ANSI string
TAG_APE = 6  # APE tags : series of null-terminated UTF-8 strings
TAG_MP4 = 7  # MP4/iTunes metadata : series of null-terminated UTF-8 strings
TAG_WMA = 8  # WMA tags : series of null-terminated UTF-8 strings
TAG_VENDOR = 9  # OGG encoder : UTF-8 string
TAG_LYRICS3 = 10  # Lyric3v2 tag : ASCII string
TAG_CA_CODEC = 11  # CoreAudio codec info : TAG_CA_CODEC structure
TAG_MF = 13  # Media Foundation tags : series of null-terminated UTF-8 strings
TAG_WAVEFORMAT = 14  # WAVE format : WAVEFORMATEEX structure
TAG_AM_MIME = 15  # Android Media MIME type : ASCII string
TAG_AM_NAME = 16  # Android Media codec name : ASCII string
TAG_RIFF_INFO = 0x100  # RIFF "INFO" tags : series of null-terminated ANSI strings
TAG_RIFF_BEXT = 0x101  # RIFF/BWF "bext" tags : TAG_BEXT structure
TAG_RIFF_CART = 0x102  # RIFF/BWF "cart" tags : TAG_CART structure
TAG_RIFF_DISP = 0x103  # RIFF "DISP" text tag : ANSI string
TAG_RIFF_CUE = 0x104  # RIFF "cue " chunk : TAG_CUE structure
TAG_RIFF_SMPL = 0x105  # RIFF "smpl" chunk : TAG_SMPL structure
TAG_APE_BINARY = 0x1000  # + index #, binary APE tag : TAG_APE_BINARY structure
TAG_MUSIC_NAME = 0x10000  # MOD music name : ANSI string
TAG_MUSIC_MESSAGE = 0x10001  # MOD message : ANSI string
TAG_MUSIC_ORDERS = 0x10002  # MOD order list : BYTE array of pattern numbers
TAG_MUSIC_AUTH = 0x10003  # MOD author : UTF-8 string
TAG_MUSIC_INST = 0x10100  # + instrument #, MOD instrument name : ANSI string
TAG_MUSIC_SAMPLE = 0x10300  # + sample #, MOD sample name : ANSI string
