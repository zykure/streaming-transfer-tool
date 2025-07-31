import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from artist_widget import ArtistWidget
from album_widget import AlbumWidget
from track_widget import TrackWidget
from playlist_widget import PlaylistWidget

#############################################################################

gMainWindow: QMainWindow|None = None

#############################################################################

class IdMappingTable():

    FILENAME = "saved-id-mappings.json"

    def __init__(self, parent):
        self.parent = parent

        self.data = {
            'artist': {},
            'album':  {},
            'track':  {},
        }

    def add(self, type: str, idA: str, idB: str):
        if type not in self.data:
            raise KeyError(f"unknown mapping type: {type}")

        # add mapping
        app_key = f'{self.parent.appA.name}:{self.parent.appB.name}'
        if app_key not in self.data[type]:
            self.data[type][app_key] = {}

        self.data[type][app_key][idA] = idB

        # add reverse mapping
        rev_app_key = f'{self.parent.appB.name}:{self.parent.appA.name}'
        if rev_app_key not in self.data[type]:
            self.data[type][rev_app_key] = {}

        self.data[type][rev_app_key][idB] = idA

    def find(self, type: str, idA: str):
        if type not in self.data:
            raise KeyError(f"unknown mapping type: {type}")

        app_key = f'{self.parent.appA.name}:{self.parent.appB.name}'
        if app_key not in self.data[type]:
            return None

        if idA not in self.data[type]:
            return None

        # return mapping
        idB = self.data[type][idA]
        return idB

    def save(self):
        print("Saving mapping table ...")
        with open(self.FILENAME, 'w', encoding='utf8') as f:
            json.dump(self.data, f, indent=2)

    def load(self):
        print("Loading mapping table ...")
        try:
            with open(self.FILENAME, 'r', encoding='utf8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            return
        except json.decoder.JSONDecodeError:
            return


#############################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        global gMainWindow
        gMainWindow = self

        super().__init__()

        self.appA = None
        self.appB = None

        self.mappingTable = IdMappingTable(self)
        self.mappingTable.load()

        # Overview page
        self.wAppInfoLabelA = QLabel()
        self.wAppInfoLabelA.setStyleSheet("QLabel {font-size: 16pt; }")
        
        self.wAppInfoLabelB = QLabel()
        self.wAppInfoLabelB.setStyleSheet("QLabel {font-size: 16pt; }")
        
        self.wOverviewLayout = QGridLayout()
        self.wOverviewLayout.addWidget(self.wAppInfoLabelA, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.wOverviewLayout.addWidget(self.wAppInfoLabelB, 0, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        
        self.wOverviewWidget = QWidget(self)
        self.wOverviewWidget.setLayout(self.wOverviewLayout)

        # Artists page
        self.wArtistWidget = ArtistWidget(self)

        # Albums page
        self.wAlbumWidget = AlbumWidget(self)

        # Tracks page
        self.wTrackWidget = TrackWidget(self)

        # Playlists page
        self.wPlaylistWidget = PlaylistWidget(self)

        self.wStatusBar = self.statusBar()

        # Main window
        self.wTabWidget = QTabWidget()
        self.wTabWidget.addTab(self.wOverviewWidget, 'Overview')
        self.wTabWidget.addTab(self.wArtistWidget, 'Artists')
        self.wTabWidget.addTab(self.wAlbumWidget, 'Albums')
        self.wTabWidget.addTab(self.wTrackWidget, 'Tracks')
        self.wTabWidget.addTab(self.wPlaylistWidget, 'Playlists')
        #self.wTabWidget.setStyleSheet("QTabBar::tab {min-width: 100px; max-width: 400px;}");

        self.setWindowTitle("Streaming Transfer Tool")
        self.setCentralWidget(self.wTabWidget)
        self.resize(1000, 600);
        self.showMaximized()

    def closeEvent(self, event):
        self.mappingTable.save()

    def showMessage(self, msg, timeout=4000):
        print(msg)
        if self.wStatusBar:
            self.wStatusBar.showMessage(msg, timeout)

    def setAppA(self, app):
        self.appA = app
        
        self.wAppInfoLabelA.setText(
            f"<b>Service: {self.appA.name}</b><br/><br/>"
            f"User ID: {self.appA.uid}<br/>"
            f"Display Name: {self.appA.display_name}<br/>"
        )

        self.wArtistWidget.reset()
        self.wAlbumWidget.reset()
        self.wTrackWidget.reset()
        self.wPlaylistWidget.reset()

    def setAppB(self, app):
        self.appB = app

        self.wAppInfoLabelB.setText(
            f"<b>Service: {self.appB.name}</b><br/><br/>"
            f"User ID: {self.appB.uid}<br/>"
            f"Display Name: {self.appB.display_name}<br/>"
        )

        self.wArtistWidget.reset()
        self.wAlbumWidget.reset()
        self.wTrackWidget.reset()
        self.wPlaylistWidget.reset()
