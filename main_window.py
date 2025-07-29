from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from artist_widget import ArtistWidget
from album_widget import AlbumWidget

#############################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.src_app = None
        self.dst_app = None
        
        # Artists page
        self.artistWidget = ArtistWidget(self)
        
        # Albums page
        self.albumWidget = AlbumWidget(self)
        
        # Tracks page
        self.trackWidget = QWidget()
        
        # Playlists page
        self.playlistWidget = QWidget()
        
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

    def set_src_app(self, app):
        self.src_app = app
        
        self.artistWidget.refresh()
        self.albumWidget.refresh()
        #self.trackWidget.refresh()
        #self.playlistWidget.refresh()
        
    def set_dst_app(self, app):
        self.dst_app = app
                
        self.artistWidget.refresh()
        self.albumWidget.refresh()
        #self.trackWidget.refresh()
        #self.playlistWidget.refresh()
        