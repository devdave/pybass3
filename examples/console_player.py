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
    print("Playing: ", song_file)
    print(f"Bytes: {song.remaining_bytes=}")

    while song.remaining_bytes > 0:
        print(song.position_time, "/", song.duration_time)
        time.sleep(1)

    print("Song finished")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("song_file")
    args = parser.parse_args()

    main(args.song_file)