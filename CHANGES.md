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