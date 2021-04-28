import dataclasses
import ctypes
from pathlib import Path

from PySide2 import QtCore
from PySide2 import QtWidgets


from bass_module import bass_module, func_type, Bass
from bass_stream import BassStream
from bass_channel import BassChannel

from codes import errors

from song import Song


QT = QtCore.Qt

get_error_description = errors.get_description


class Simple(QtWidgets.QWidget):

    def __init__(self, song_file):
        super(Simple, self).__init__()
        self.song_file = song_file
        self.song = Song(song_file)

        self.setupUI()
        self.connectUI()

        self.song.position_updated.connect(self.on_song_position_updated)

    def on_song_position_updated(self, seconds):
        self.duration.setText(repr(seconds))


    def setupUI(self):

        self.load_file = QtWidgets.QPushButton("Load song")
        self.play_btn = QtWidgets.QPushButton("Play")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.duration = QtWidgets.QLabel("0000")
        self.length = QtWidgets.QLabel("0000")
        self.table = QtWidgets.QTableWidget(1, 2)
        self.configureTable()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.load_file)
        vbox.addWidget(self.play_btn)
        vbox.addWidget(self.stop_btn)
        vbox.addWidget(self.pause_btn)
        vbox.addWidget(self.duration)
        vbox.addWidget(self.length)
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


    def on_play_clicked(self):
        print("Play clicked")
        self.length.setText(repr(self.song.seconds))
        self.song.play()

    def on_stop_clicked(self):
        print("Stop clicked")
        self.song.stop()

    def on_pause_clicked(self):
        print("Pause clicked")
        self.song.pause()

    def on_load_song_clicked(self):
        fileDialog = QtWidgets.QFileDialog(self)
        supportedMimeTypes = ['audio/mpeg', 'application/ogg', 'application/octet-stream']
        fileDialog.setMimeTypeFilters(supportedMimeTypes)
        # fileDialog.setFileMode(fileDialog.Directory & fileDialog.ExistingFile)
        if fileDialog.exec_() == QtWidgets.QDialog.Accepted:
            files = fileDialog.selectedFiles()
            file = files[0]
            if self.song is not None:
                self.song.stop()
                del self.song

            self.song = Song(file)
            self.duration.setText(str(self.song.seconds))
            self.song.play()



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
