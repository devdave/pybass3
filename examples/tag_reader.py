import argparse
from pathlib import Path

from pybass3 import Bass, BassChannel, BassStream
from pybass3.structs.id import ID3v1
from pybass3.codes.tag import ID3


def b2u(val):
    return val.decode("utf8")


def main(song_file):
    Bass.Init()
    song_file = Path(song_file)
    print("Parsing: %s" % song_file)
    song_posix = bytes(song_file)
    handle = BassStream.CreateFile(False, song_posix)
    tag_info = BassChannel.GetID3v1Tags(handle)
    print(f"{tag_info.contents.artist} - {tag_info.contents.album}")
    print(f"{tag_info.contents.title}")





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file")
    args = parser.parse_args()

    main(args.song_file)
