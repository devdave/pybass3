PyBASS wrapper
--------------

# LICENSING

The PyBass PYTHON wrapper is licensed under the MIT license BUT the BASS Library is dual licensed as free to use
for non-commercial development but requires a license for paid/commercial work.   Please see http://un4seen.com

#BASS library documentation

http://www.un4seen.com/doc/

# Purpose and notes

A simple wrapper around un4seen.com's BASS audio library to enable playing various format media files from python.


#Stock python usage

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

