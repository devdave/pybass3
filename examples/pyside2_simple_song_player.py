import dataclasses
import ctypes
from pathlib import Path

from PySide2 import QtCore
from PySide2 import QtWidgets

from pybass3.pys2_song import Pys2Song
from pybass3.codes import errors
from pybass3 import Bass
from pybass3.bass_module import BassException



QT = QtCore.Qt

get_error_description = errors.get_description


class Simple(QtWidgets.QWidget):

    def __init__(self, song_file):
        super(Simple, self).__init__()
        self.song_file = song_file
        self.song = Pys2Song(song_file)

        self.slide_mousedown = False

        self.setupUI()
        self.connectUI()

        self.song.position_updated.connect(self.on_song_position_updated)
        self.position_slide.setRange(0, self.song.duration)

    def on_song_position_updated(self, seconds):
        self.position.setText(repr(seconds))
        self.position_slide.setSliderPosition(self.song.position)

    def on_position_slider_changed(self):
        if self.slide_mousedown is True:
            value = self.position_slide.value()
            self.song.move2position_seconds(value)



    def setupUI(self):

        self.load_file = QtWidgets.QPushButton("Load song")
        self.play_btn = QtWidgets.QPushButton("Play")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.position = QtWidgets.QLabel("0000")
        self.length = QtWidgets.QLabel("0000")
        self.position_slide = QtWidgets.QSlider(QT.Horizontal)
        self.table = QtWidgets.QTableWidget(1, 2)
        self.configureTable()

        vbox = QtWidgets.QVBoxLayout()
        time_box = QtWidgets.QHBoxLayout()
        vbox.addWidget(self.load_file)
        vbox.addWidget(self.play_btn)
        vbox.addWidget(self.stop_btn)
        vbox.addWidget(self.pause_btn)
        time_box.addWidget(self.position)
        time_box.addWidget(self.length)
        vbox.addLayout(time_box)
        vbox.addWidget(self.position_slide)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def add_table_row(self, row_id, label, value):
        label_item = QtWidgets.QTableWidgetItem(label)
        value_item = QtWidgets.QTableWidgetItem(value)
        self.table.setItem(row_id, 0, label_item)
        self.table.setItem(row_id, 1, value_item)


    def configureTable(self):
        columns = ["Name", "Value"]
        self.table.setHorizontalHeaderLabels(columns)
        row_id = 0

        lib_info = Bass.GetLibInfo()

        def advance_row(row_id):
            row_id = row_id + 1
            return row_id

        lib_fields = ["flags", "hwsize", "hwfree", "freesam", "free3d", "minrate", "maxrate", "eax", "minbuf", "dsver",
                  "latency", "initflags", "speakers", "freq"]

        device_fields = ["name", "driver", "flags"]

        self.table.setRowCount(len(lib_fields)+1+len(device_fields)+1)

        self.add_table_row(0, "Library info", "")
        for pos, field_name in enumerate(lib_fields, 1):
            field_value = getattr(lib_info, field_name)
            print(field_name, str(field_value))

            self.add_table_row(pos, field_name, repr(field_value))

        # IMPORTANT, fucking kill this struct as soon as possible to avoid memory leaks
        del lib_info

        device_info = Bass.GetDeviceInfo()

        self.add_table_row(len(lib_fields)+1,"Device info", "")
        for pos, field_name, in enumerate(device_fields, len(lib_fields)+2):
            field_value = getattr(device_info, field_name)
            self.add_table_row(pos, field_name, repr(field_value))



        self.table.resizeColumnsToContents()


    def connectUI(self):
        self.play_btn.clicked.connect(self.on_play_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        self.load_file.clicked.connect(self.on_load_song_clicked)

        self.position_slide.sliderPressed.connect(self.on_position_slider_mousdown)
        self.position_slide.sliderReleased.connect(self.on_position_slider_mouseup)

        self.position_slide.valueChanged.connect(self.on_position_slider_changed)


    def on_play_clicked(self):
        print("Play clicked")
        try:
            self.length.setText(repr(self.song.duration))
            self.song.play()
        except BassException as bexc:
            box = QtWidgets.QMessageBox()
            box.setText(f"Unable to play file {self.song.file_path} - Error is {bexc.desc}")
            box.exec_()

    def on_stop_clicked(self):
        print("Stop clicked")
        self.song.stop()

    def on_pause_clicked(self):
        print("Pause clicked")
        self.song.pause()

    def on_load_song_clicked(self):
        fileDialog = QtWidgets.QFileDialog(self)
        supportedMimeTypes = ['audio/mpeg', 'application/ogg', 'audio/ogg', 'application/octet-stream']
        fileDialog.setMimeTypeFilters(supportedMimeTypes)
        # fileDialog.setFileMode(fileDialog.Directory & fileDialog.ExistingFile)
        fileDialog.setDirectory(self.song.file_path.parent.as_posix())
        if fileDialog.exec_() == QtWidgets.QDialog.Accepted:
            files = fileDialog.selectedFiles()
            file = files[0]
            if self.song is not None:
                del self.song

            self.song = QtSong(file)
            # Assure the song loads correctly
            try:
                self.song.handle is not None
            except BassException as bexc:
                box = QtWidgets.QMessageBox()
                box.setText(f"Unable to load {file=} because {bexc.desc}")
                box.exec_()
            else:
                self.song.position_updated.connect(self.on_song_position_updated)
                self.position_slide.setRange(0, self.song.duration)
                self.song.play()
                seconds = self.song.duration
                self.length.setText(str(seconds))

    def on_position_slider_mousdown(self):
        self.slide_mousedown = True

    def on_position_slider_mouseup(self):
        self.slide_mousedown = False



def main(song_file):
    app = QtWidgets.QApplication()
    player = Simple(song_file)
    player.show()
    return app.exec_()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("song_file")
    args = parser.parse_args()

    main(args.song_file)
