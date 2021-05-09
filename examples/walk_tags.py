from pathlib import Path
import argparse

from pybass3 import BassException
from pybass3.song import Song

def walk_directory(directory: Path) -> (float, int, int):
    valid_types = [".ogg", ".mp3", ".mp4"]
    files = (element for element in directory.iterdir() if element.is_file() and element.suffix in valid_types)
    dirs = (element for element in directory.iterdir() if element.is_dir())

    accum_time = 0
    success = 0
    fail = 0

    for file in files:
        song = Song(file)
        try:
            out = f"({song.duration_time}) {song.tags['artist']} - {song.tags['title']} => {song.file_path.as_posix()!r}"
            print(out)
            accum_time += song.duration
            success += 1
        except BaseException as exc:
            fail += 1
            if exc.code == 41:
                print(f"Failed to process {song.file_path.as_posix()} - invalid format")



    for sub_dir in dirs:
        a, s, f = walk_directory(sub_dir)
        accum_time += a
        success += s
        fail += f

    return accum_time, success, fail

def main(search_path: Path):

    assert search_path.is_dir()
    print("Starting from %s" % search_path)
    time, success, fail = walk_directory(search_path)
    hours = int(time // 60)
    minutes = int(time % 60)
    print(f"Total play time: {hours:02}:{minutes:02} - {success=} & {fail=}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_dir")
    args = parser.parse_args()

    main(Path(args.song_dir))

