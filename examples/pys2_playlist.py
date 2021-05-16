import sys
import pathlib
import time
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
Qt = QtCore.Qt

from pybass3 import BassException
from pybass3.pys2_playlist import Pys2Playlist
from pybass3.pys2_song import Pys2Song


log = logging.getLogger(__name__)


class PlayerWindow(QtWidgets.QMainWindow):

    pl_position: QtWidgets.QLabel
    song_title: QtWidgets.QLabel
    song_position: QtWidgets.QLabel
    song_duration: QtWidgets.QLabel
    seek_bar: QtWidgets.QSlider
    prv_btn: QtWidgets.QPushButton
    ply_btn: QtWidgets.QPushButton
    pause_btn: QtWidgets.QPushButton
    stop_btn: QtWidgets.QPushButton
    next_btn: QtWidgets.QPushButton
    add_file_btn: QtWidgets.QPushButton
    add_dir_btn: QtWidgets.QPushButton


    def __init__(self, *args, **kwargs):
        super(PlayerWindow, self).__init__(*args, **kwargs)
        self.pl_position = None
        self.song_title = None
        self.song_position = None
        self.song_duration = None
        self.seek_bar = None
        self.prv_btn = self.ply_btn = self.pause_btn = self.stop_btn = self.next_btn = None
        self.add_file_btn = self.add_dir_btn = None
        self.setupUI()

        log.debug("Initialized PlayerWindow")

    def setupUI(self):
        frame = QtWidgets.QFrame()
        vbox = QtWidgets.QVBoxLayout(frame)

        self.pl_position = QtWidgets.QLabel("Playlist position")
        vbox.addWidget(self.pl_position)

        self.song_title = QtWidgets.QLabel("Song: ")
        vbox.addWidget(self.song_title)

        time_line_box = QtWidgets.QHBoxLayout()

        self.song_position = QtWidgets.QLabel("00:00")
        time_line_box.addWidget(self.song_position)

        self.song_duration = QtWidgets.QLabel("99:99")
        time_line_box.addWidget(self.song_duration)

        vbox.addLayout(time_line_box)

        self.seek_bar = QtWidgets.QSlider(Qt.Horizontal)
        vbox.addWidget(self.seek_bar)

        control_box = QtWidgets.QHBoxLayout(frame)

        self.prv_btn = QtWidgets.QPushButton("Previous")
        self.ply_btn = QtWidgets.QPushButton("Play")
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.next_btn = QtWidgets.QPushButton("Next")

        for button in [self.prv_btn, self.ply_btn, self.pause_btn, self.stop_btn, self.next_btn]:
            control_box.addWidget(button)
        vbox.addLayout(control_box)

        add_box = QtWidgets.QHBoxLayout(frame)

        self.add_file_btn = QtWidgets.QPushButton("Add file")
        self.add_dir_btn = QtWidgets.QPushButton("Add directory")

        for button in [self.add_file_btn, self.add_dir_btn]:
            add_box.addWidget(button)

        vbox.addLayout(add_box)

        queue_box = QtWidgets.QHBoxLayout()
        self.randomize_btn = QtWidgets.QPushButton("Randomize")
        self.sequential_btn = QtWidgets.QPushButton("Sequential")
        queue_box.addWidget(self.randomize_btn)
        queue_box.addWidget(self.sequential_btn)

        vbox.addLayout(queue_box)


        frame.setLayout(vbox)
        self.setCentralWidget(frame)

        log.debug("PlayerWindow - UI is setup")



class PlayerController(QtCore.QObject):

    def __init__(self):
        super(PlayerController, self).__init__()
        self.view = PlayerWindow()
        self.playlist = Pys2Playlist()

        self.seek_bar_pressed = False

        log.debug("PlayerController initialzied")

        self.connect()

    def connect(self):

        connection = self.view.prv_btn.clicked.connect(self.playlist.previous)

        self.view.prv_btn.clicked.connect(self.on_prv_clicked)
        self.view.ply_btn.clicked.connect(self.on_play_clicked)
        self.view.pause_btn.clicked.connect(self.on_pause_clicked)
        self.view.stop_btn.clicked.connect(self.on_stop_clicked)
        self.view.next_btn.clicked.connect(self.on_next_clicked)

        self.view.seek_bar.sliderPressed.connect(self.on_seek_mousedown)
        self.view.seek_bar.sliderReleased.connect(self.on_seek_mouseup)
        self.view.seek_bar.valueChanged.connect(self.on_seek_change)

        self.view.add_file_btn.clicked.connect(self.do_add_file)
        self.view.add_dir_btn.clicked.connect(self.do_add_directory)

        self.view.randomize_btn.clicked.connect(self.on_randomize_click)
        self.view.sequential_btn.clicked.connect(self.on_sequential_click)

        #Playlist connections
        self.playlist.signals.ticked.connect(self.on_pl_tick)
        self.playlist.signals.song_changed.connect(self.on_song_changed)

        log.debug("PlayerController connected to view")

    def on_prv_clicked(self):
        log.debug("PlayerController.on_prv_clicked")
        self.playlist.previous()

    def on_play_clicked(self):
        log.debug("PlayerController.on_play_clicked")
        self.playlist.play()

    def on_pause_clicked(self):
        log.debug("PlayerController.on_pause_clicked")
        self.playlist.pause()

    def on_stop_clicked(self):
        log.debug("PlayerController.on_stop_clicked")
        self.playlist.stop()

    def on_next_clicked(self):
        log.debug("PlayerController.on_next_clicked")
        self.playlist.next()

    def on_seek_mousedown(self):
        self.seek_bar_pressed = True

    def on_seek_mouseup(self):
        self.seek_bar_pressed = False

    def on_seek_change(self, value):
        if self.seek_bar_pressed is True and self.playlist.current is not None:
            self.playlist.current.move2position_bytes(value)


    def on_pl_tick(self):
        self.do_state_update()

    def on_song_changed(self, song_id):
        log.debug("PlayerController.on_song_changed")
        song = self.playlist.get_song_by_id(song_id)
        if song is not None:
            log.debug("new song position to duration - %s to %s",
                      song.position_bytes,
                      song.duration_bytes
                      )
            self.view.seek_bar.setRange(0, song.duration_bytes)
            self.view.seek_bar.setValue(song.position_bytes)

    def do_state_update(self):
        # Add 1 to queue position because it starts counting from 0
        self.view.pl_position.setText(f"{self.playlist.queue_position+1}/{len(self.playlist.queue)}({len(self.playlist)})")
        if self.playlist.current is not None:
            song_name = self.playlist.current.file_path.name
            song_pos = self.playlist.current.position_time
            song_len = self.playlist.current.duration_time
            song_val = self.playlist.current.position_bytes
        else:
            song_name = "Nothing playing"
            song_pos = "0:00"
            song_len = "0:00"
            song_val = 0

        self.view.song_title.setText(song_name)
        self.view.song_position.setText(song_pos)
        self.view.song_duration.setText(song_len)
        self.view.seek_bar.setValue(song_val)


    def do_add_file(self):
        log.debug("PlayerController.do_add_file")

        name_filters = [
            "Audio files (*.wav *.mp3 *.mp4 *.ogg)",
            "Any files (*)"
        ]

        music_dir = (pathlib.Path.home() / "music").as_posix()

        song_file = QtWidgets.QFileDialog.getOpenFileName(
            self.view,
            "Select song",
            music_dir,
            ";;".join(name_filters)
        )

        log.debug("User chose %s", song_file)

        if song_file:
            song_file = pathlib.Path(song_file[0])

            if song_file.exists() and song_file.is_file():
                song = self.playlist.add_song_by_path(song_file)
                self.do_state_update()
                self.playlist.play_song_by_id(song.id)


    def do_add_directory(self):

        log.debug("PlayerController.do_add_directory")
        music_dir = (pathlib.Path().home() / "music").as_posix()

        directory = QtWidgets.QFileDialog.getExistingDirectory(self.view,
                                                               "Select directory",
                                                               music_dir,
                                                               QtWidgets.QFileDialog.ShowDirsOnly
                                                               )

        dir_path = pathlib.Path(directory)

        log.debug("User selected %s", dir_path)

        if dir_path.exists():
            self.playlist.add_directory(dir_path, recurse=True)
            if len(self.playlist) > 0:
                self.playlist.play()

        self.do_state_update()

    def on_randomize_click(self):
        self.playlist.stop()

        self.playlist.set_randomize()

        if len(self.playlist) > 0:
            self.playlist.queue_position = 0
            self.playlist.play()

    def on_sequential_click(self):
        self.playlist.stop()

        self.playlist.set_sequential()

        if len(self.playlist) > 0:
            self.playlist.queue_position = 0
            self.playlist.play()


def setup_logging():

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    pass

def main():
    setup_logging()
    log.info("Example Pyside2 player started!")

    app = QtWidgets.QApplication()
    player = PlayerController()
    player.view.show()

    app.exec_()


if __name__ == "__main__":
    main()