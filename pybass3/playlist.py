
import enum
from pathlib import Path

from .song import Song

try:
    import PySide2
except ImportError
    HAS_PYSIDE2 = False


class PlaylistState(enum.Enum):
    stopped = enum.auto()
    playing = enum.auto()
    paused = enum.auto()
    error = enum.auto()

class PlaylistMode(enum.Enum):
    loop_single = enum.auto()
    loop_all = enum.auto()
    one_time = enum.auto()

    sequential = enum.auto()
    random = enum.auto()

class Playlist:

    VALID_TYPES = ["mp3", "mp4", "ogg", "opus"]

    songs:list # The songs the playlist knows about
    queue: list # The order songs will be played in
    state: PlaylistState # Is the playlist playing songs, stopped, or paused?
    mode: PlaylistMode # Is the playlist running sequential or random
    play_mode: PlaylistMode # is the playlist looping the whole queue, just a song, or running to end?

    queue_position: int  # Where is the playlist in the current queue
    current_song: Song # What is currently playing
    fadein_song: Song # if fade_in is not None, this is the next song to play
    fade_in: int # How soon should the next song start playing, None if lock step
    song_cls: Song # What is the container for a song (eg Song or QtSong)



    def __init__(self, song_cls = Song):
        self.songs = []
        self.queue = []
        self.state = PlaylistState.stopped
        self.mode = PlaylistMode.sequential

        self.queue_position = None
        self.current_song = None
        self.upcoming_song = None
        self.fade_in = None
        self.song_cls = Song

    def add_song(self, song_path):
        song = self.song_cls(song_path)
        self.songs.append(song)

    def add_directory(self, dir_path: Path, recurse=True):
        files = (file for file in dir_path.iterdir() if file.is_file() and file.suffix)
        dirs = (fdir for fdir in dir_path.iterdir() if fdir.is_dir())

        for song_path in files:
            self.add_song(song_path)

        if recurse is True:
            for fdir in dirs:
                self.add_directory(fdir, recurse)

    def set_fade(self, seconds):
        self.fade_in = seconds

    def randomize(self):
        ids = range(0, len(self.songs))





