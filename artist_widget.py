from PyQt6.QtCore import Qt, QPoint, QAbstractTableModel
from PyQt6.QtWidgets import *

from util import *

#############################################################################

class Artist:
    def __init__(self, id: str, name: str):
        self.id = id
        self._name = name.strip()
        
    @staticmethod
    def fromItem(item):
        obj = Artist(id=item.id, name=item.name)        
        return obj
                
    @property
    def name(self):
        return self._name
        
    def simplifiedName(self):
        return simplifiedName(self.name)
        
    def sortKey(self):
        return (self._name.lower(),)

#############################################################################

class ArtistModel(QAbstractTableModel):
    
    COLUMNS = ['id', 'name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clear()
                
    def setSiblingModel(self, model: "ArtistModel"):
        self.sibling = model
      
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.artists[index.row()].id
            elif index.column() == 1:
                return self.artists[index.row()]._name
                
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
        return len(self.artists)
        
    def columnCount(self, index):
        return len(self.COLUMNS)
  
    def clear(self):
        self.artists = []
        self.names = []
        
    def add(self, item: Artist):
        self.artists.append(item)
        self.names = [ x.name.lower() for x in self.artists ]

    def find(self, name: str):
        if name.lower() not in self.names:
            return None
        index = self.names.index(name.lower())
        return self.artists[index]
        
#############################################################################

class ArtistWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        
        self.wButtonLoadSrc = QPushButton('< Load')
        self.wButtonLoadDst = QPushButton('Load >')
        self.wButtonTransfer = QPushButton('>> Transfer >>')
        self.wButtonRevTransfer = QPushButton('<< Transfer <<')

        self.wButtonLayout = QGridLayout()
        self.wButtonLayout.setContentsMargins(20, 100, 20, 100);
        self.wButtonLayout.addWidget(self.wButtonLoadSrc, 3, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.wButtonLayout.addWidget(self.wButtonLoadDst, 3, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.wButtonLayout.addWidget(self.wButtonTransfer, 8, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.wButtonLayout.addWidget(self.wButtonRevTransfer, 9, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        
        self.wButtonLoadSrc.clicked.connect(self.loadSrcData)
        self.wButtonLoadDst.clicked.connect(self.loadDstData)
        self.wButtonTransfer.clicked.connect(self.transferSrcToDst)
        self.wButtonRevTransfer.clicked.connect(self.transferDstToSrc)
        
        self.wTableModelSrc = ArtistModel()
        self.wTableViewSrc = QTableView()
        self.wTableViewSrc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableViewSrc.verticalHeader().hide()
        self.wTableViewSrc.setModel(self.wTableModelSrc)
        
        self.wTableModelDst = ArtistModel()
        self.wTableViewDst = QTableView()
        self.wTableViewDst.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableViewDst.verticalHeader().hide()
        self.wTableViewDst.setModel(self.wTableModelDst)
        
        self.wTableViewSrc.verticalScrollBar().valueChanged.connect(self.scrollSrcTable)
        self.wTableViewDst.verticalScrollBar().valueChanged.connect(self.scrollDstTable)

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
   
    def reset(self):
        """Clear table data and reset widgets."""
        
        self.wTableModelSrc.clear()
        self.wTableModelDst.clear()

        if self.parent.src_app:
            self.wLabelSrc.setText(self.parent.src_app.name)
        if self.parent.dst_app:
            self.wLabelDst.setText(self.parent.dst_app.name)

    def scrollSrcTable(self):
        """Synchronize Dst with Src scroll bar."""
        
        self._scrollTable(self.wTableViewSrc, self.wTableModelSrc,
                          self.wTableViewDst, self.wTableModelDst)
        
    def scrollDstTable(self):
        """Synchronize Src with Dst scroll bar."""
        
        self._scrollTable(self.wTableViewDst, self.wTableModelDst,
                          self.wTableViewSrc, self.wTableModelSrc)

    def loadSrcData(self):
        """Load Src table."""
        
        self._loadArtists(self.parent.src_app, self.wTableModelSrc)
        
        self.wTableModelSrc.layoutChanged.emit()
        self.wTableModelDst.layoutChanged.emit()
        
    def loadDstData(self):
        """Load Dst table."""
        
        self._loadArtists(self.parent.dst_app, self.wTableModelDst)
        
        self.wTableModelSrc.layoutChanged.emit()
        self.wTableModelDst.layoutChanged.emit()
        
    def transferSrcToDst(self):
        """Transfer items from Src to Dst."""
        
        self._transferArtists(self.parent.src_app, self.wTableModelSrc,
                              self.parent.dst_app, self.wTableModelDst)

        self.wTableModelDst.layoutChanged.emit()
        
    def transferDstToSrc(self):
        """Transfer items from Dst to Src."""
        
        self._transferArtists(self.parent.dst_app, self.wTableModelDst,
                              self.parent.src_app, self.wTableModelSrc)
        
        self.wTableModelSrc.layoutChanged.emit()

    def _scrollTable(self, 
                     src_view: QTableView, src_model: QAbstractTableModel, 
                     dst_view: QTableView, dst_model: QAbstractTableModel):
        
        s_row = src_view.indexAt(QPoint(0, 0)).row()  # top row
        if s_row:
            name = src_model.names[s_row]
            if name in dst_model.names:
                d_row = dst_model.names.index(name)
                if d_row:
                    dst_view.scrollTo(dst_model.createIndex(d_row, 0))
                    dst_view.update()

    def _loadArtists(self, app, model: QAbstractTableModel):
        
        model.clear()

        self.parent.showMessage(f"\nLoading {app.name} artists ...")
        items = app.get_saved_artists()
        artists = sorted([Artist.fromItem(x) for x in items], 
                         key=lambda x: x.sortKey())
        
        print(f"=> Artists ({len(artists)}):")
        for artist in artists:
            self.parent.showMessage(f"Loaded artist: {artist.name}")
            model.add(artist)

    def _transferArtists(self, 
                         src_app, src_model: QAbstractTableModel, 
                         dst_app, dst_model: QAbstractTableModel):
        
        new_id_list = []  # collected artist id's to add
        
        cancel = False    # true if operation cancelled by user
        for s_artist in src_model.artists:
            s_name = s_artist.simplifiedName()
            s_id = s_artist.id

            # Skip already added artists
            d_artist = dst_model.find(s_name)
            if d_artist:
                d_id = str(d_artist.id)
                self.parent.mapping_table.add('artist', s_id, d_id)
                continue
                
            self.parent.showMessage(f"Transfer artist: {s_name} ({src_app.name}:{s_id})")

            # Re-use known mapping
            d_id = self.parent.mapping_table.find('artist', s_id)
            if d_id:
                self.parent.showMessage(f"Transfer artist: {s_name} ({src_app.name}:{s_id}) => {d_name} ({dst_app.name}:{d_id}) [restored]")
                new_id_list.append(d_id)
                continue

            # Search by artist name
            result = dst_app.search_artist(s_name)
            artists = [Artist.fromItem(x) for x in result]

            # Find matching artist in search results
            match = False
            for d_artist in artists:
                d_name = d_artist.simplifiedName()

                # Must have exact, case-insensitive match
                if d_name.lower() == s_name.lower():
                    d_id = str(d_artist.id)
                    
                    self.parent.showMessage(f"Transfer artist: {s_name} ({src_app.name}:{s_id}) => {d_name} ({dst_app.name}:{d_id}) [matched]")
                    new_id_list.append(d_id)
                    self.parent.mapping_table.add('artist', s_id, d_id)
                    
                    match = True
                    break

            if not match:
                # Allow to manually specify an artist id
                dlg = QInputDialog(self)                 
                #dlg.setInputMode(QInputDialog.TextInput) 
                dlg.setWindowTitle(f"Artist not found on {dst_app.name}")
                dlg.setLabelText(f"Artist NOT FOUND!\n{s_name}\n\nPlease provide id manually (leave empty to skip):")                        
                dlg.resize(400, 100)
                
                if dlg.exec():
                    # Get artist by id
                    d_id = dlg.textValue().strip()
                    if d_id:                    
                        d_artist = dst_app.get_artist(d_id)
                        if d_artist:
                            d_name = d_artist.simplifiedName()

                            # Add saved artist
                            self.parent.showMessage(f"Adding artist: {s_name} ({src_app.name}:{s_id}) => {d_name} ({dst_app.name}:{d_id}) [manual]")
                            new_id_list.append(d_id)
                            self.parent.mapping_table.add('artist', s_id, d_id)

                else:
                    cancel = True
                    break
                    
        if cancel:
            return
        
        print(f"Adding {len(new_id_list)} artists to {dst_app.name} ...")
        if dst_app.add_saved_artist(new_id_list):
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText(f"{len(new_id_list)} artist(s) were added to {self.parent.dst_app.name}.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            
            self._loadArtists(dst_app, dst_model)
