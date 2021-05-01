"""
Dirt simple command line music/sound file player.

Makes 0(zero) effort to handle unexpected bugs for the sake of
clarity.

"""
from argparse import ArgumentParser

from pybass3 import Song
import time

def main(song_file):
    song = Song(song_file)
    song.play()
    len_bytes = song.duration_bytes
    position_bytes = song.position_bytes
    print("Playing: ", song_file)
    print(f"Bytes: {len_bytes=}")

    while position_bytes < len_bytes:
        print(song.position, song.duration)
        time.sleep(1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("song_file")
    args = parser.parse_args()

    main(args.song_file)