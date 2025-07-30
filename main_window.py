import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from artist_widget import ArtistWidget
from album_widget import AlbumWidget
from track_widget import TrackWidget
from playlist_widget import PlaylistWidget

#############################################################################

class IdMappingTable():

    FILENAME = "saved-id-mappings.json"

    def __init__(self, parent):
        self.parent = parent

        self.mappingTable = {
            'artist': {},
            'album':  {},
            'track':  {},
        }

    def add(self, type: str, idA: str, idB: str):
        if type not in self.mappingTable:
            raise KeyError(f"unknown mapping type: {type}")

        # add mapping
        app_key = f'{self.parent.appA.name}:{self.parent.appB.name}'
        if app_key not in self.mappingTable[type]:
            self.mappingTable[type][app_key] = {}

        self.mappingTable[type][app_key][idA] = idB

        # add reverse mapping
        rev_app_key = f'{self.parent.appB.name}:{self.parent.appA.name}'
        if rev_app_key not in self.mappingTable[type]:
            self.mappingTable[type][rev_app_key] = {}

        self.mappingTable[type][rev_app_key][idB] = idA

    def find(self, type: str, idA: str):
        if type not in self.mappingTable:
            raise KeyError(f"unknown mapping type: {type}")

        app_key = f'{self.parent.appA.name}:{self.parent.appB.name}'
        if app_key not in self.mappingTable[type]:
            return None

        if idA not in self.mappingTable[type]:
            return None

        # return mapping
        idB = self.mappingTable[type][idA]
        return idB

    def save(self):
        print("Saving mapping table ...")
        with open(self.FILENAME, 'w', encoding='utf8') as f:
            json.dump(self.mappingTable, f)

    def load(self):
        print("Loading mapping table ...")
        try:
            with open(self.FILENAME, 'r', encoding='utf8') as f:
                self.mappingTable = json.load(f)
        except FileNotFoundError:
            return
        except json.decoder.JSONDecodeError:
            return


#############################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.appA = None
        self.appB = None

        self.mappingTable = IdMappingTable(self)
        self.mappingTable.load()

        # Artists page
        self.artistWidget = ArtistWidget(self)

        # Albums page
        self.albumWidget = AlbumWidget(self)

        # Tracks page
        self.trackWidget = TrackWidget(self)

        # Playlists page
        self.playlistWidget = PlaylistWidget(self)

        self.statusBar = self.statusBar()

        # Main window
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.artistWidget, 'Artists')
        self.tabWidget.addTab(self.albumWidget, 'Albums')
        self.tabWidget.addTab(self.trackWidget, 'Tracks')
        self.tabWidget.addTab(self.playlistWidget, 'Playlists')
        #self.tabWidget.setStyleSheet("QTabBar::tab {min-width: 100px; max-width: 400px;}");

        self.setWindowTitle("Streaming Transfer Tool")
        self.setCentralWidget(self.tabWidget)
        self.resize(1000, 600);
        self.showMaximized()

    def closeEvent(self, event):
        self.mappingTable.save()

    def showMessage(self, msg, timeout=4000):
        print(msg)
        if self.statusBar:
            self.statusBar.showMessage(msg, timeout)

    def setAppA(self, app):
        self.appA = app

        self.artistWidget.reset()
        self.albumWidget.reset()
        self.trackWidget.reset()
        self.playlistWidget.reset()

    def setAppB(self, app):
        self.appB = app

        self.artistWidget.reset()
        self.albumWidget.reset()
        self.trackWidget.reset()
        self.playlistWidget.reset()
