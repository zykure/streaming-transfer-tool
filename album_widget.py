from PyQt6.QtCore import Qt, QPoint, QAbstractTableModel
from PyQt6.QtWidgets import *
from collections import namedtuple

from util import *

#############################################################################

Album = namedtuple('Album', 'id name artist')

albumName = lambda x: x.artist.strip() + " - " + x.name.strip()

class AlbumModel(QAbstractTableModel):
    
    COLUMNS = ['id', 'name', 'artist']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clear()
                
    def setSiblingModel(self, model: "AlbumModel"):
        self.sibling = model
      
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.albums[index.row()].id
            elif index.column() == 1:
                return self.albums[index.row()].name
            elif index.column() == 2:
                return self.albums[index.row()].artist
                
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.names[index.row()] in self.sibling.names:
                return MyColors.Green.value
            else:
                return MyColors.Orange.value
            
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]            
        return super().headerData(section, orientation, role)
        
    def rowCount(self, index):
        return len(self.albums)
        
    def columnCount(self, index):
        return len(self.COLUMNS)
  
    def clear(self):
        self.albums = []
        self.names = []
        
    def add(self, item: Album):
        self.albums.append(item)
        self.names = [ albumName(x).lower() for x in self.albums ]
        
        
#############################################################################

class AlbumWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        
        self.wButtonLoadSrc = QPushButton('< Load')
        self.wButtonLoadDst = QPushButton('Load >')
        self.wButtonTransfer = QPushButton('>> Transfer >>')

        self.wButtonLayout = QGridLayout()
        self.wButtonLayout.setContentsMargins(20, 100, 20, 100);
        self.wButtonLayout.addWidget(self.wButtonLoadSrc, 3, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.wButtonLayout.addWidget(self.wButtonLoadDst, 3, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.wButtonLayout.addWidget(self.wButtonTransfer, 8, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        
        self.wButtonLoadSrc.clicked.connect(self.load_albums_src)
        self.wButtonLoadDst.clicked.connect(self.load_albums_dst)
        self.wButtonTransfer.clicked.connect(self.transfer_albums)
        
        self.wTableModelSrc = AlbumModel()
        self.wTableViewSrc = QTableView()
        self.wTableViewSrc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableViewSrc.verticalHeader().hide()
        self.wTableViewSrc.setModel(self.wTableModelSrc)
        
        self.wTableModelDst = AlbumModel()
        self.wTableViewDst = QTableView()
        self.wTableViewDst.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableViewDst.verticalHeader().hide()
        self.wTableViewDst.setModel(self.wTableModelDst)
        
        self.wTableViewSrc.verticalScrollBar().valueChanged.connect(self.scroll_albums_src)
        self.wTableViewDst.verticalScrollBar().valueChanged.connect(self.scroll_albums_dst)

        self.wTableModelSrc.setSiblingModel(self.wTableModelDst)
        self.wTableModelDst.setSiblingModel(self.wTableModelSrc)
        
        self.wLabelSrc = QLabel()
        self.wLabelSrc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wLabelSrc.setStyleSheet("QLabel {font-size: 400%; font-weight: bold; text-align: center}");
        
        self.wLayoutSrc = QVBoxLayout()
        self.wLayoutSrc.addWidget(self.wLabelSrc)
        self.wLayoutSrc.addWidget(self.wTableViewSrc)
        
        self.wLabelDst = QLabel()
        self.wLabelDst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wLabelDst.setStyleSheet("QLabel {font-size: 400%; font-weight: bold; text-align: center}");
        
        self.wLayoutDst = QVBoxLayout()
        self.wLayoutDst.addWidget(self.wLabelDst)
        self.wLayoutDst.addWidget(self.wTableViewDst)

        self.wLayout = QHBoxLayout()
        self.wLayout.addLayout(self.wLayoutSrc)
        self.wLayout.addLayout(self.wButtonLayout)
        self.wLayout.addLayout(self.wLayoutDst)
        
        self.setLayout(self.wLayout)
 
    def refresh(self):
        self.wTableModelSrc.clear()
        self.wTableModelDst.clear()

        if self.parent.src_app:
            self.wLabelSrc.setText(self.parent.src_app.name)
        if self.parent.dst_app:
            self.wLabelDst.setText(self.parent.dst_app.name)

    def scroll_albums_src(self):
        s_row = self.wTableViewSrc.indexAt(QPoint(0, 0)).row()  # top row
        if s_row:
            name = self.wTableModelSrc.names[s_row]
            if name in self.wTableModelDst.names:
                d_row = self.wTableModelDst.names.index(name)
                if d_row:
                    self.wTableViewDst.scrollTo(self.wTableModelDst.createIndex(d_row, 0))
                    self.wTableViewDst.update()
        
    def scroll_albums_dst(self):
        s_row = self.wTableViewDst.indexAt(QPoint(0, 0)).row()  # top row
        if s_row:
            name = self.wTableModelDst.names[s_row]
            if name in self.wTableModelSrc.names:
                d_row = self.wTableModelSrc.names.index(name)
                if d_row:
                    self.wTableViewSrc.scrollTo(self.wTableModelSrc.createIndex(d_row, 0))
                    self.wTableViewSrc.update()

    def load_albums_src(self):
        self.wTableModelSrc.clear()

        print(f"\nLoading {self.parent.src_app.name} albums ...")
        items = self.parent.src_app.get_saved_albums()
        items = sorted(items, key=lambda x: (x.artists[0].name.lower(), x.name.lower()))
        
        print(f"=> Albums ({len(items)}):")
        for item in items:
            print(f"\t{item.name}")
            self.wTableModelSrc.add(Album(id=item.id, name=item.name.strip(), artist=item.artists[0].name.strip()))

        # Trigger refresh
        self.wTableModelSrc.layoutChanged.emit()
        self.wTableModelDst.layoutChanged.emit()
        
    def load_albums_dst(self):
        self.wTableModelDst.clear()

        print(f"\nLoading {self.parent.dst_app.name} albums ...")
        items = self.parent.dst_app.get_saved_albums()
        items = sorted(items, key=lambda x: (x.artists[0].name.lower(), x.name.lower()))
        
        print(f"=> Albums ({len(items)}):")
        for item in items:
            print(f"\t{item.name}")
            self.wTableModelDst.add(Album(id=item.id, name=item.name.strip(), artist=item.artists[0].name.strip()))
        
        # Trigger refresh
        self.wTableModelDst.layoutChanged.emit()
        self.wTableModelSrc.layoutChanged.emit()
        
    def transfer_albums(self):
        print("\nProcessing missing albums:")
        
        new_id_list = []  # collected album id's to add
        cancel = False    # true if operation cancelled by user
        for s_album in self.wTableModelSrc.albums:
            s_name = simplifiedName(albumName(s_album))
            s_id = s_album.id

            # Skip already added albums
            if s_name.lower() in self.wTableModelDst.names:
                continue

            # Search by album name
            print(f"+ [add] {s_name} ({self.parent.src_app.name}:{s_id})")
            result = self.parent.dst_app.search_album(s_name)

            # Find matching album in search results
            match = False
            for d_album in result:
                d_name = simplifiedName(albumName(d_album))
                d_id = str(d_album.id)

                # Must have exact, case-insensitive match
                if d_name.lower() == s_name.lower():
                    d_id = str(d_album.id)
                    print(f"\t{d_name} ({self.parent.dst_app.name}:{d_id})")
                    new_id_list.append(d_id)
                    
                    match = True
                    break

            if not match:
                # Allow to manually specify an album id
                dlg = QInputDialog(self)                 
                #dlg.setInputMode(QInputDialog.TextInput) 
                dlg.setWindowTitle(f"Album not found on {self.parent.dst_app.name}")
                dlg.setLabelText(f"Album NOT FOUND!\n{s_name}\n\nPlease provide id manually:")                        
                dlg.resize(400, 100)
                
                if dlg.exec():
                    # Get album by id
                    d_id = dlg.textValue().strip()
                    if d_id:                    
                        d_album = self.parent.dst_app.get_album(d_id)
                        if d_album:
                            d_name = simplifiedName(albumName(d_album))

                            # Add saved album
                            print(f"\t{d_name} ({self.parent.dst_app.name}:{d_id})")
                            new_id_list.append(d_id)

                else:
                    cancel = True
                    break
                    
        if cancel:
            return
        
        print(f"Adding {len(new_id_list)} albums to {self.parent.dst_app.name} ...")
        if self.parent.dst_app.add_saved_album(new_id_list):
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText(f"{len(new_id_list)} album(s) were added to {self.parent.dst_app.name}.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()