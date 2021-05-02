import pathlib
import typing
import logging
import sys

import PySide2
from PySide2 import QtWidgets
from PySide2 import QtCore

Qt = QtCore.Qt

from pybass3.pys2_playlist import Pys2Playlist
from pybass3.pys2_song import Pys2Song
from pybass3 import BassException

log = logging.getLogger(__name__)

class PlaylistModel(QtCore.QAbstractTableModel):



    record_added = QtCore.Signal(int)



    def __init__(self, playlist: Pys2Playlist):
        super(PlaylistModel, self).__init__()
        self.playlist = playlist
        log.debug("initialized")



    def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        # log.debug("headerData called with %s, %s, %s", section, orientation, role)
        if role == Qt.DisplayRole:
            if section == 0:
                return "RID"
            elif section == 1:
                return "Length"
            elif section == 2:
                return "Name"

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        """
        Song ID, Song length, Song file name

        :param parent:
        :return:
        """
        return 3

    def rowCount(self, parent:PySide2.QtCore.QModelIndex=...) -> int:
        # log.debug("rowCount has #%s rows", len(self.playlist))
        return len(self.playlist)

    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:
        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return row
            else:
                song = self.playlist.songs[row]
                if col == 1:
                    return song.duration
                elif col == 2:
                    return song.file_path.name
        elif role == Qt.ToolTipRole:
            if col == 2:
                song = self.playlist.songs[row]
                return song.file_path.as_posix()

    def add_song(self, song_id, song, play_on_add=True):
        log.debug("Adding song %s - %s", song_id, song)
        rowCount = song_id
        last = rowCount
        self.beginInsertRows(QtCore.QModelIndex(), rowCount, last)

        self.endInsertRows()
        if play_on_add is True:
            self.playlist.play_song(song_id)

        self.record_added.emit(song_id)




class PlayerControl(QtCore.QObject):

    playlist: Pys2Playlist
    model: PlaylistModel
    progress_mousedown: bool


    def __init__(self):
        super(PlayerControl, self).__init__()
        self.playlist = Pys2Playlist()
        self.model = PlaylistModel(self.playlist)

        self.progress_mousedown = False
        self.view = PlayerView(self.model)
        self.connectUI()

    def connectUI(self):
        self.view.progress.sliderPressed.connect(self.on_progress_mouseup)
        self.view.progress.sliderReleased.connect(self.on_progress_mousedown)
        self.view.progress.valueChanged.connect(self.on_progress_changed)

        self.view.prev_btn.clicked.connect(self.on_prev_clicked)
        self.view.play_btn.clicked.connect(self.on_play_clicked)
        self.view.pause_btn.clicked.connect(self.on_pause_clicked)
        self.view.stop_btn.clicked.connect(self.on_stop_clicked)
        self.view.next_btn.clicked.connect(self.on_next_clicked)

        self.view.add_file_btn.clicked.connect(self.on_add_song_clicked)

    @QtCore.Slot()
    def on_progress_mouseup(self):
        log.debug("on_progress_mouseup")
        self.progress_mousedown = False

    @QtCore.Slot()
    def on_progress_mousedown(self):
        log.debug("on_progress_mousedown")
        self.progress_mousedown = True

    @QtCore.Slot()
    def on_progress_changed(self):
        if self.progress_mousedown is True:
            if self.playlist.current is not None:
                self.playlist.current.move2position_bytes(self.view.progress.value())

    @QtCore.Slot()
    def on_prev_clicked(self):
        self.playlist.previous()


    @QtCore.Slot()
    def on_play_clicked(self):
        self.playlist.play()

    @QtCore.Slot()
    def on_pause_clicked(self):
        self.playlist.pause()

    @QtCore.Slot()
    def on_stop_clicked(self):
        self.playlist.stop()

    @QtCore.Slot()
    def on_next_clicked(self):
        self.playlist.next()

    @QtCore.Slot()
    def on_add_song_clicked(self):
        fileDialog = QtWidgets.QFileDialog(self.view)
        supportedMimeTypes = ['application/octet-stream']
        fileDialog.setMimeTypeFilters(supportedMimeTypes)
        if fileDialog.exec_() == QtWidgets.QDialog.Accepted:
            files = fileDialog.selectedFiles()
            file = files[0]
            # Assure the song loads correctly
            try:
                index, song = self.playlist.add_song(file)
                song.handle is not None
                song.free_stream()
            except BassException as bexc:
                box = QtWidgets.QMessageBox()
                box.setText(f"Unable to load {file=} because {bexc.desc}")
                box.exec_()
            else:

                song.position_updated.connect(self.on_progress_changed)
                seconds = song.duration
                self.view.progress.setRange(0, seconds)
                self.view.duration.setText(str(seconds))
                self.model.add_song(index, song)
                self.playlist.play()





class PlayerView(QtWidgets.QMainWindow):

    def __init__(self, model: PlaylistModel):
        super(PlayerView, self).__init__()
        self.model = model

        self.setupUI()
        self.configureTable(model)

    def setupUI(self) -> None:
        """
            Layout sketch
            -------------

            Song file name
            position text / duration text
            <previous> <play> <pause> <stop> <next>
            [Play list table]

        :return:
        """

        body = QtWidgets.QFrame()
        vbox = QtWidgets.QVBoxLayout()

        self.song_title = QtWidgets.QLabel("Song title")
        vbox.addWidget(self.song_title)

        stat_line = QtWidgets.QHBoxLayout()
        self.position = QtWidgets.QLabel("0:00")
        stat_line.addWidget(self.position)

        self.progress = QtWidgets.QSlider(Qt.Horizontal)
        stat_line.addWidget(self.progress)

        self.duration = QtWidgets.QLabel("0:00")
        stat_line.addWidget(self.duration)


        vbox.addLayout(stat_line)

        cmd_line = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton("Previous")
        cmd_line.addWidget(self.prev_btn)

        self.play_btn = QtWidgets.QPushButton("Play")
        cmd_line.addWidget(self.play_btn)

        self.pause_btn = QtWidgets.QPushButton("Pause")
        cmd_line.addWidget(self.pause_btn)

        self.stop_btn = QtWidgets.QPushButton("Stop")
        cmd_line.addWidget(self.stop_btn)

        self.next_btn = QtWidgets.QPushButton("Next")
        cmd_line.addWidget(self.next_btn)

        vbox.addLayout(cmd_line)

        self.table = QtWidgets.QTableView()
        vbox.addWidget(self.table)

        play_list_ctrls = QtWidgets.QHBoxLayout()
        self.randomize_btn = QtWidgets.QPushButton("Sequential")
        self.randomize_btn.setCheckable(True)
        play_list_ctrls.addWidget(self.randomize_btn)

        self.repeat_btn = QtWidgets.QPushButton("Loop")
        self.repeat_btn.setCheckable(True)
        play_list_ctrls.addWidget(self.repeat_btn)

        self.clear_btn = QtWidgets.QPushButton("Clear")
        play_list_ctrls.addWidget(self.clear_btn)

        self.add_file_btn = QtWidgets.QPushButton("Add song")
        play_list_ctrls.addWidget(self.add_file_btn)

        self.add_dir_btn = QtWidgets.QPushButton("Add directory")
        play_list_ctrls.addWidget(self.add_dir_btn)

        vbox.addLayout(play_list_ctrls)

        body.setLayout(vbox)
        self.setCentralWidget(body)

    def configureTable(self, playlist_obj):

        self.table.setModel(self.model)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().hide()

        self.model.record_added.connect(self.on_new_song)

    def on_new_song(self, rid = None):
        log.debug("Song added successfully, queuing to play %s", rid)
        if rid:
            pass


        self.table.resizeColumnsToContents()

def main():

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(levelname)s:%(name)s:%(funcName)s@%(lineno)s - %(message)s")
    log.info("Starting")

    app = QtWidgets.QApplication()
    control = PlayerControl()
    control.view.show()

    app.exec_()
    log.info("Shutting down")

if __name__ == "__main__":
    main()