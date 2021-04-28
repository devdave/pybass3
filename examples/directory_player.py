import pathlib
import time
import argparse
import msvcrt

from pybass3 import Song
from pybass3.playlist import Playlist




def kbfunc():
    x = msvcrt.kbhit()
    if x:
       ret = ord(msvcrt.getch())
    else:
       ret = 0

    return ret


def main(dir_path):
    dir_path = pathlib.Path(dir_path)

    playlist = Playlist()
    playlist.add_directory(dir_path, recurse=True)

    playlist.play()
    play_indefinitely = True
    while play_indefinitely:
        try:
            print(playlist.current.file_path.name, playlist.current_song.position, playlist.current_song.duration)
            playlist.tick()
            key = kbfunc()
            if key:
                print("User pressed", key)
                if key == 122:
                    playlist.previous()
                elif key == 98:
                    playlist.next()
                elif key == 120:
                    playlist.play()
                elif key == 99:
                    playlist.pause()
                elif key == 118:
                    playlist.stop()

            time.sleep(1)
        except KeyboardInterrupt:
            playlist.free()
            play_indefinitely = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_dir")
    args = parser.parse_args()

    main(args.song_dir)