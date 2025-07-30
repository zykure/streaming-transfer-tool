from enum import Enum
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QColor

from item_types import _TypeTemplate

#############################################################################

class MyColors(Enum):
    Blue   = QColor(48, 159, 219)
    Green  = QColor(129, 187, 95)
    Yellow = QColor(251, 206, 74)
    Orange = QColor(237, 129, 62)
    Red    = QColor(233, 91, 84)
    Pink   = QColor(232, 93, 136)
    Purple = QColor(133, 78, 155)

#############################################################################

class _ModelTemplate(QAbstractTableModel):

    COLUMNS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.names = []
        self.ids   = []
        self.siblingModel = None

    def setSiblingModel(self, model: "_ModelTemplate"):
        self.siblingModel = model

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]
        return super().headerData(section, orientation, role)

    def rowCount(self, index):
        return len(self.items)

    def columnCount(self, index):
        return len(self.COLUMNS)

    def clear(self):
        self.items = []
        self.names = []
        self.ids   = []

    def add(self, item: _TypeTemplate):
        self.items.append(item)
        self.names = [ x.simplifiedName().lower() for x in self.items ]
        self.ids = [ x.id for x in self.items ]

    def insert(self, item: _TypeTemplate):
        self.items.insert(0, item)
        self.names = [ x.simplifiedName().lower() for x in self.items ]
        self.ids = [ x.id for x in self.items ]

    def find(self, name: str):
        if name.lower() not in self.names:
            return None
        index = self.names.index(name.lower())
        return self.items[index]

#############################################################################

class ArtistModel(_ModelTemplate):

    COLUMNS = ['id', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.items[index.row()].id
            elif index.column() == 1:
                return self.items[index.row()]._name

        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.items[index.row()].dirty:
                return MyColors.Yellow.value
            elif self.names[index.row()] in self.siblingModel.names:
                return MyColors.Green.value
            else:
                return MyColors.Orange.value

#############################################################################

class AlbumModel(_ModelTemplate):

    COLUMNS = ['id', 'name', 'artist']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.items[index.row()].id
            elif index.column() == 1:
                return self.items[index.row()]._name
            elif index.column() == 2:
                return self.items[index.row()].artist

        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.items[index.row()].dirty:
                return MyColors.Yellow.value
            elif self.names[index.row()] in self.siblingModel.names:
                return MyColors.Green.value
            else:
                return MyColors.Orange.value

#############################################################################

class TrackModel(_ModelTemplate):

    COLUMNS = ['id', 'name', 'artist', 'album']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.items[index.row()].id
            elif index.column() == 1:
                return self.items[index.row()]._name
            elif index.column() == 2:
                return self.items[index.row()].artist
            elif index.column() == 3:
                return self.items[index.row()].album

        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.items[index.row()].dirty:
                return MyColors.Yellow.value
            elif self.names[index.row()] in self.siblingModel.names:
                return MyColors.Green.value
            else:
                return MyColors.Orange.value

#############################################################################

class PlaylistModel(_ModelTemplate):

    COLUMNS = ['id', 'name', 'description', 'num_tracks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.items[index.row()].id
            elif index.column() == 1:
                return self.items[index.row()]._name
            elif index.column() == 2:
                return self.items[index.row()].description
            elif index.column() == 3:
                return self.items[index.row()].numTracks()

        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.items[index.row()].dirty:
                return MyColors.Yellow.value
            elif self.names[index.row()] in self.siblingModel.names:
                return MyColors.Green.value
            else:
                return MyColors.Orange.value
