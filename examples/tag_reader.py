import argparse



def main(song_file):
    print("Parsing: %s" % song_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file")
    args = parser.parse_args()

    main(args.song_file)
