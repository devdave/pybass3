# PyBASS wrapper

[![Downloads](https://pepy.tech/badge/pybass3)](https://pepy.tech/project/pybass3)


LICENSING
---------

The PyBass PYTHON wrapper is licensed under the MIT license.  Meanwhile the BASS C Library is dual licensed as free to use
for non-commercial development but requires a license for paid/commercial work.   Please see http://un4seen.com

BASS library documentation
---------------------------

http://www.un4seen.com/doc/

Purpose and notes
------------------

A simple wrapper around un4seen.com's BASS audio library to enable playing various format media files from python.

Stock python usage
------------------

```python
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
```

# Windows playlist example

```python
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
            print(playlist.current.file_path.name, playlist.current.position, playlist.current.duration)
            playlist.tick()
            key = kbfunc()
            if key:                
                if key == 122: # Z
                    print("Previous")
                    playlist.previous()
                elif key == 98: # B                    
                    print("Next")
                    playlist.next()
                elif key == 120: # X
                    print("Play")
                    playlist.play()
                elif key == 99: # c
                    print("Pause")    
                    playlist.pause()
                elif key == 118: # v
                    print("Stop")
                    playlist.stop()
            else:
                time.sleep(1)
                
        except KeyboardInterrupt:
            playlist.free()
            play_indefinitely = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_dir")
    args = parser.parse_args()

    main(args.song_dir)
```
