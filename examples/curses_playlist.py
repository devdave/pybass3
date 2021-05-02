"""
    Run a basic playlist controlled player in curses
    `python -m pip install windows-curses`
"""
import argparse
import curses
import pathlib
import time

from pybass3.playlist import Playlist
from pybass3 import Song

SCREEN = None

def init():
    global SCREEN
    if SCREEN is None:
        SCREEN = curses.initscr()
        curses.noecho()
        curses.cbreak()
        SCREEN.nodelay(True)
        SCREEN.keypad(True)
        curses.curs_set(False)


    return SCREEN

def shutdown():
    global SCREEN
    if SCREEN is not None:
        curses.echo()
        curses.nocbreak()
        SCREEN.nodelay(False)
        SCREEN.keypad(False)
        curses.curs_set(True)
        curses.endwin()
        SCREEN = None

def f2t(raw): # Float To Time
    seconds = int(raw % 60)
    minutes = int(raw // 60)
    return f"{minutes:02}:{seconds:02}"

def print_centered_text(window, line_pos, text, display_width):
    middle = max(0, (display_width // 2) - len(text) // 2)
    window.addstr(line_pos, middle, text)


def main(song_dir):
    screen = init()
    screen.clear()
    playlist = Playlist()

    playlist.add_directory(pathlib.Path(song_dir))

    playlist.play()

    display = curses.newwin(10, 120, 0, 0)

    keep_playing = True
    while keep_playing is True:

        try:
            key = screen.getkey()
        except:
            key = None

        if key == "q":
            keep_playing = False
        elif key == "z":
            playlist.previous()
        elif key == "x":
            playlist.play()
        elif key == "c":
            playlist.pause()
        elif key == "v":
            playlist.stop()
        elif key == "b":
            playlist.next()
        elif key == "d":
            # Move forward N seconds
            song = playlist.current
            new_position = min(song.duration, song.position + 10)
            song.move2position_seconds(new_position)
        elif key == "a":
            # Move backward N seconds
            song = playlist.current
            new_position = max(0, song.position - 10)
            song.move2position_seconds(new_position)

        elif key == "r":
            playlist.set_randomize()
            playlist.stop()
            playlist.queue_position = 0
            playlist.play()
        elif key == "s":
            playlist.set_sequential()
            playlist.stop()
            playlist.queue_position = 0
            playlist.play()



        song = playlist.current

        display.clear()
        display.border('|', '|', '-', '-', '+', '+', '+', '+')

        playcount = f"Playlist position: {playlist.queue_position+1}/{len(playlist.queue)}"
        print_centered_text(display, 0, playcount, 120)

        filename = f"Song: {song.file_path.name}"
        print_centered_text(display, 1, filename, 120)

        counter = f"{f2t(song.position)} / {f2t(song.duration)}"
        print_centered_text(display, 2, counter, 120)

        perc_done = (song.position_bytes / song.duration_bytes)

        progress_perc = f"{int(100 * perc_done)}%"
        tick_end = int(89*perc_done)
        progress_line = "=" * tick_end
        display.addstr(3, 10, "[")
        display.addstr(3, 11, progress_line)
        display.addstr(3, 100, "]")

        print_centered_text(display, 3, progress_perc, 120)

        control1 = "Z - Previous; X - Play; C - Pause; V - Stop; B - Next"
        control2 = "A - Back 10 seconds; D - Forward 10 seconds"
        control3 = "S - Sequential playlist;  R - random playlist"
        control4 = "Q - Quit"

        for pos, line in enumerate([control1, control2, control3, control4], 5):
            print_centered_text(display, pos, line, 120)

        display.refresh()
        curses.napms(750)
        playlist.tick()

    shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("song_dir")
    args = parser.parse_args()
    try:
        main(args.song_dir)
        print("Program exited gracefully")
    finally:
        shutdown()



