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
    STATUS_INDICATORS = [ '+', 'o', 'x' ]  # modified/matching/not matching
    STATUS_COLORS =  [ MyColors.Yellow.value, MyColors.Green.value, MyColors.Orange.value ]

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

    def getRowStatus(self, row):
        if self.items[row].dirty:
            return 0  # modified
        elif self.names[row] in self.siblingModel.names:
            return 1  # matching
        else:
            return 2  # not matching

    def rowCount(self, index):
        return len(self.items)

    def columnCount(self, index):
        return len(self.COLUMNS)
        
    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        
        # sort via DSU approach
        decorated = self.sortKey(column)
        decorated.sort()
        if order == Qt.SortOrder.DescendingOrder:
            decorated.reverse()

        self.items = [item for key, i, item in decorated]
        self.update()
        self.layoutChanged.emit()
        
    def clear(self):
        self.items = []
        self.names = []
        self.ids   = []
        
    def update(self):
        self.names = [ x.simplifiedName().lower() for x in self.items ]
        self.ids = [ x.id for x in self.items ]

    def add(self, item: _TypeTemplate):
        self.items.append(item)
        self.update()

    def insert(self, item: _TypeTemplate):
        self.items.insert(0, item)
        self.update()

    def find(self, name: str):
        if name.lower() not in self.names:
            return None
        index = self.names.index(name.lower())
        return self.items[index]

#############################################################################

class ArtistModel(_ModelTemplate):

    COLUMNS = ['id', 'name', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.items[index.row()].id
            elif index.column() == 1:
                return self.items[index.row()]._name
            elif index.column() == 2:
                return self.STATUS_INDICATORS[self.getRowStatus(index.row())]

        elif role == Qt.ItemDataRole.BackgroundRole:
            return self.STATUS_COLORS[self.getRowStatus(index.row())]

    def sortKey(self, column):
        if column == 0:
            return [ ((item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 1:
            return [ ((item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 2:
            return [ ((self.getRowStatus(row), item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]

#############################################################################

class AlbumModel(_ModelTemplate):

    COLUMNS = ['id', 'name', 'artist', 'status']

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
                return self.STATUS_INDICATORS[self.getRowStatus(index.row())]

        elif role == Qt.ItemDataRole.BackgroundRole:
            return self.STATUS_COLORS[self.getRowStatus(index.row())]

    def sortKey(self, column):
        if column == 0:
            return [ ((item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 1:
            return [ ((item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 2:
            return [ ((item.artist, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 3:
            return [ ((self.getRowStatus(row), item.artist, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]

#############################################################################

class TrackModel(_ModelTemplate):

    COLUMNS = ['id', 'name', 'artist', 'album', 'status']

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
            elif index.column() == 4:
                return self.STATUS_INDICATORS[self.getRowStatus(index.row())]

        elif role == Qt.ItemDataRole.BackgroundRole:
            return self.STATUS_COLORS[self.getRowStatus(index.row())]

    def sortKey(self, column):
        if column == 0:
            return [ ((item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 1:
            return [ ((item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 2:
            return [ ((item.artist, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 3:
            return [ ((item.album, item.artist, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 4:
            return [ ((self.getRowStatus(row), item.album, item.artist, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]

#############################################################################

class PlaylistModel(_ModelTemplate):

    COLUMNS = ['id', 'name', 'description', 'public', 'num_tracks', 'status']

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
                return 'yes' if self.items[index.row()].public else 'no'
            elif index.column() == 4:
                return self.items[index.row()].numTracks()
            elif index.column() == 5:
                return self.STATUS_INDICATORS[self.getRowStatus(index.row())]

        elif role == Qt.ItemDataRole.BackgroundRole:
            return self.STATUS_COLORS[self.getRowStatus(index.row())]

    def sortKey(self, column):
        if column == 0:
            return [ ((item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 1:
            return [ ((item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 2:
            return [ ((item.description, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 3:
            return [ ((item.public, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 4:
            return [ ((item.num_tracks, item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
        elif column == 5:
            return [ ((self.getRowStatus(row), item._name, item.id), row, item)
                     for row, item in enumerate(self.items) ]
