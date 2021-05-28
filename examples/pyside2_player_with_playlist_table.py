import typing
import sys
import pathlib
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets

from pybass3.pys2_playlist import Pys2Playlist as Playlist

Qt = QtCore.Qt
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
    randomize_btn: QtWidgets.QPushButton
    sequential_btn: QtWidgets.QPushButton
    pl_table: QtWidgets.QTableView

    def __init__(self, *args, **kwargs):
        super(PlayerWindow, self).__init__(*args, **kwargs)

        self.setupUI()

        log.debug("Initialized PlayerWindow")

    def setupUI(self):
        self.setWindowTitle("PyBASS3 - Pyside2 example")

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

        self.pl_table = QtWidgets.QTableView()
        self.pl_table.setColumnHidden(0, True)
        vbox.addWidget(self.pl_table)

        frame.setLayout(vbox)
        self.setCentralWidget(frame)

        log.debug("PlayerWindow - UI is setup")


class PlaylistTableModel(QtCore.QAbstractTableModel):

    def __init__(self, playlist):
        super(PlaylistTableModel, self).__init__()
        self.playlist = playlist

        self.playlist.signals.song_added.connect(self.song_added)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.playlist)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return 3

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            if section == 0:
                return "SID"
            elif section == 1:
                return "Name"
            elif section == 2:
                return "Time"

        return None

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> typing.Any:

        song = self.playlist.get_song_by_row(index.row())
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return song.id
            elif col == 1:
                song_name = song.title
                return song_name
            elif col == 2:
                return song.duration_time

        elif role == Qt.ToolTipRole:
            if col == 1:
                return song.file_path.as_posix()

    def song_added(self, song_id: str):

        index = self.playlist.get_indexof_song_by_id(song_id)
        log.debug("adding %s to %s", song_id, index)
        self.beginInsertRows(QtCore.QModelIndex(), index, index)
        self.endInsertRows()


class PlayerController(QtCore.QObject):

    def __init__(self):
        super(PlayerController, self).__init__()
        self.view = PlayerWindow()
        self.playlist = Playlist()
        self.plt_model = PlaylistTableModel(self.playlist)

        self.playlist.fade_in = 5

        self.seek_bar_pressed = False

        log.debug("PlayerController initialized")

        self.setup_connections()

    def setup_connections(self):

        # self.view.prv_btn.clicked.connect(self.playlist.previous)
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

        # Playlist connections
        self.playlist.signals.ticked.connect(self.on_pl_tick)
        self.playlist.signals.song_changed.connect(self.on_song_changed)

        # I could hide a lot of view logic as a PlayerWindow set model method
        # but I am tired of how complicated this has gotten
        self.view.pl_table.setModel(self.plt_model)
        self.view.pl_table.hideColumn(0)
        self.view.pl_table.verticalHeader().hide()
        self.view.pl_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.view.pl_table.doubleClicked.connect(self.on_songs_table_row_clicked)

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

        song_index = self.playlist.get_indexof_song_by_id(song_id)
        self.view.pl_table.selectRow(song_index)
        self.view.pl_table.resizeColumnsToContents()

    def do_state_update(self):
        # Add 1 to queue position because it starts counting from 0
        self.view.pl_position.setText(
            f"{self.playlist.queue_position + 1}/{len(self.playlist.queue)}({len(self.playlist)})")
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
                if song:
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
            self.playlist.add_directory(dir_path, recurse=True, suppress_emit=False)
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
        # self.playlist.stop()

        self.playlist.set_sequential(restart_and_play=False)

        # if len(self.playlist) > 0:
        #     self.playlist.queue_position = 0
        #     self.playlist.play()

    def on_songs_table_row_clicked(self):
        index = self.view.pl_table.selectedIndexes()[0]  # type: QtCore.QModelIndex
        self.playlist.play_song_by_index(index.row())
        log.debug("%s was clicked", index)


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
