import pathlib
import typing

import PySide2
from PySide2 import QtWidgets
from PySide2 import QtCore

Qt = QtCore.Qt


class PlaylistModel(QtCore.QAbstractTableModel):

    def __init__(self, playlist):
        self.playlist = playlist

    def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
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


        pass




class PlayerView(QtWidgets.QMainWindow):

    def __init__(self):
        super(PlayerList, self).__init__()

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
