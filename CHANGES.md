Version change history
======================

0.0.2
-----

* Split apart Song and QtSong into their own files.
* Renamed QtSong to Pys2Song to reflect it is intended for Pyside2 and not PyQt5
    1. Split into separate files
* Added a python curses powered music player.
* Song (and child classes) now have a uuid4 .id property

* Multiple bug fixes


0.0.3
-----
* Semi-flaky/rough draft playlist controlled
 QT app example added
  
* Multiple adjustments and tuning to playlist to resolve
next and transition logic.
  
* Multiple fixes to Pys2Playlist so that it behaves
correctly.
  
* Finished a working example of using a QTableView with Pys2Playlist.   It's amazing how much more scaffolding and
supporting logic goes into wiring this up.
  
* current_song property/variable is dead & gone, the correct property is now `current` which handles memory/handle cleanup
and keeps things kosher.
  
0.1.0
-----

* Add support for BASS_GetTags along with a default
helper to fetch (artist, album, year, track, and genre)
  
* Various code cleanup

* `add_song` has changed so that it takes a `Song` object and adds that to the playlist/queue while the original method
has been renamed to `add_song_by_path`
  
* Refactored Signals to be consolidated into an adjacent "<ClassName>Signals" class to make it easier to see what signals
a given class emits.
  
* Refactoring to get rid of camelCase convention in my code in favor of snake_case.

* Refactoring Pys2_\* classes to be compatible with both PyQT5 and Pyside2 via the qtd.py module.
  