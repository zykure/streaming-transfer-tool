from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from artist_widget import ArtistWidget
from album_widget import AlbumWidget
from track_widget import TrackWidget

#############################################################################

class IdMappingTable():
    
    FILENAME = "saved-id-mappings.json"
    
    def __init__(self, parent):
        self.parent = parent
        
        self.mapping_table = {
            'artist': {},
            'album':  {},
            'track':  {},
        }
    
    def add(self, type: str, src_id: str, dst_id: str):
        if type not in self.mapping_table:
            raise KeyError(f"unknown mapping type: {type}")

        # add mapping
        app_key = f'{self.parent.src_app.name}:{self.parent.dst_app.name}'
        if app_key not in self.mapping_table[type]:
            self.mapping_table[type][app_key] = {}
            
        self.mapping_table[type][app_key][src_id] = dst_id
        
        # add reverse mapping
        rev_app_key = f'{self.parent.dst_app.name}:{self.parent.src_app.name}'
        if rev_app_key not in self.mapping_table[type]:
            self.mapping_table[type][rev_app_key] = {}
            
        self.mapping_table[type][rev_app_key][dst_id] = src_id
        
    def find(self, type: str, src_id: str):
        if type not in self.mapping_table:
            raise KeyError(f"unknown mapping type: {type}")
            
        app_key = f'{self.parent.src_app.name}:{self.parent.dst_app.name}'
        if app_key not in self.mapping_table[type]:
            return None
            
        if src_id not in self.mapping_table[type]:
            return None
        
        # return mapping
        dst_id = self.mapping_table[type][src_id]
        return dst_id
    
    def save(self):
        with open(self.FILENAME, 'w') as f:
            json.dump(f, self.mapping_table)
            
    def load(self):
        try:
            with open(self.FILENAME, 'r') as f:
                self.mapping_table = json.load(f)
        except FileNotFoundError as e:
            return
            
      
#############################################################################
  
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.src_app = None
        self.dst_app = None
        
        self.mapping_table = IdMappingTable(self)
        self.mapping_table.load()
        
        # Artists page
        self.artistWidget = ArtistWidget(self)
        
        # Albums page
        self.albumWidget = AlbumWidget(self)
        
        # Tracks page
        self.trackWidget = TrackWidget(self)
        
        # Playlists page
        self.playlistWidget = QWidget()
        
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
        pass
    
    def showMessage(self, msg, timeout=4000):
        print(msg)
        self.statusBar.showMessage(msg, timeout)
      
    def setSrcApp(self, app):
        self.src_app = app
        
        self.artistWidget.reset()
        self.albumWidget.reset()
        self.trackWidget.reset()
        #self.playlistWidget.reset()
        
    def setDstApp(self, app):
        self.dst_app = app
                
        self.artistWidget.reset()
        self.albumWidget.reset()
        self.trackWidget.reset()
        #self.playlistWidget.reset()
        