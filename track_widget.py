from PyQt6.QtCore import Qt, QPoint, QAbstractTableModel
from PyQt6.QtWidgets import *
from collections import namedtuple

from util import *

#############################################################################

class Track:
    def __init__(self, id: str, name: str, artist: str, album: str):
        self.id = id
        self._name = name.strip()
        self._artist = artist.strip()
        self._album = album.strip()
        
    @staticmethod
    def fromItem(item):
        obj = Track(id=item.id, name=item.name, artist=item.artists[0].name, album=item.album.name)        
        return obj

    @property
    def name(self):
        return self._artist + " - " + self._name

    def simplifiedName(self):
        return simplifiedName(self.name)
        
    def sortKey(self):
        return (self._artist.lower(), self._name.lower(), self._album.lower())

#############################################################################

class TrackModel(QAbstractTableModel):
    
    COLUMNS = ['id', 'name', 'artist', 'album']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clear()
                
    def setSiblingModel(self, model: "TrackModel"):
        self.sibling = model
      
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.tracks[index.row()].id
            elif index.column() == 1:
                return self.tracks[index.row()]._name
            elif index.column() == 2:
                return self.tracks[index.row()]._artist
            elif index.column() == 3:
                return self.tracks[index.row()]._album
                
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
        return len(self.tracks)
        
    def columnCount(self, index):
        return len(self.COLUMNS)
  
    def clear(self):
        self.tracks = []
        self.names = []
        
    def add(self, item: Track):
        self.tracks.append(item)
        self.names = [ x.name.lower() for x in self.tracks ]
                     
    def find(self, name: str):
        if name.lower() not in self.names:
            return None
        index = self.names.index(name.lower())
        return self.tracks[index]
        
#############################################################################

class TrackWidget(QWidget):
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
        
        self.wTableModelSrc = TrackModel()
        self.wTableViewSrc = QTableView()
        self.wTableViewSrc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableViewSrc.verticalHeader().hide()
        self.wTableViewSrc.setModel(self.wTableModelSrc)
        
        self.wTableModelDst = TrackModel()
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
        
        self._loadTracks(self.parent.src_app, self.wTableModelSrc)
        
        self.wTableModelSrc.layoutChanged.emit()
        self.wTableModelDst.layoutChanged.emit()
        
    def loadDstData(self):
        """Load Dst table."""
        
        self._loadTracks(self.parent.dst_app, self.wTableModelDst)
        
        self.wTableModelSrc.layoutChanged.emit()
        self.wTableModelDst.layoutChanged.emit()
        
    def transferSrcToDst(self):
        """Transfer items from Src to Dst."""
        
        self._transferTracks(self.parent.src_app, self.wTableModelSrc,
                             self.parent.dst_app, self.wTableModelDst)

        self.wTableModelDst.layoutChanged.emit()
        
    def transferDstToSrc(self):
        """Transfer items from Dst to Src."""
        
        self._transferTracks(self.parent.dst_app, self.wTableModelDst,
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

    def _loadTracks(self, app, model: QAbstractTableModel):
        
        model.clear()

        self.parent.showMessage(f"\nLoading {app.name} tracks ...")
        items = app.get_saved_tracks()
        tracks = sorted([Track.fromItem(x) for x in items], 
                         key=lambda x: x.sortKey())
        
        print(f"=> Tracks ({len(tracks)}):")
        for track in tracks:
            self.parent.showMessage(f"Loaded track: {track.name}")
            model.add(track)

    def _transferTracks(self, 
                        src_app, src_model: QAbstractTableModel, 
                        dst_app, dst_model: QAbstractTableModel):
                             
        new_id_list = []  # collected track id's to add
        
        cancel = False    # true if operation cancelled by user
        for s_track in src_model.tracks:
            s_name = s_track.simplifiedName()
            s_id = s_track.id

            # Skip already added track
            d_track = dst_model.find(s_name)
            if d_track:
                d_id = str(d_track.id)
                self.parent.mapping_table.add('track', s_id, d_id)
                continue
                
            self.parent.showMessage(f"Transfer track: {s_name} ({src_app.name}:{s_id})")

            # Re-use known mapping
            d_id = self.parent.mapping_table.find('track', s_id)
            if d_id:
                self.parent.showMessage(f"Transfer track: {s_name} ({src_app.name}:{s_id}) => {d_name} ({dst_app.name}:{d_id}) [restored]")
                new_id_list.append(d_id)
                continue

            # Search by track name
            result = dst_app.search_track(s_name)
            tracks = [Track.fromItem(x) for x in result]

            # Find matching track in search results
            match = False
            for d_track in tracks:
                d_name = d_track.simplifiedName()

                # Must have exact, case-insensitive match
                if d_name.lower() == s_name.lower():
                    d_id = str(d_track.id)
                    
                    self.parent.showMessage(f"Transfer track: {s_name} ({src_app.name}:{s_id}) => {d_name} ({dst_app.name}:{d_id}) [matched]")
                    new_id_list.append(d_id)
                    self.parent.mapping_table.add('track', s_id, d_id)
                    
                    match = True
                    break

            if not match:
                # Allow to manually specify an track id
                dlg = QInputDialog(self)                 
                #dlg.setInputMode(QInputDialog.TextInput) 
                dlg.setWindowTitle(f"Track not found on {dst_app.name}")
                dlg.setLabelText(f"Track NOT FOUND!\n{s_name}\n\nPlease provide id manually (leave empty to skip):")                        
                dlg.resize(400, 100)
                
                if dlg.exec():
                    # Get track by id
                    d_id = dlg.textValue().strip()
                    if d_id:                    
                        d_track = dst_app.get_track(d_id)
                        if d_track:
                            d_name = d_track.simplifiedName()

                            # Add saved track
                            self.parent.showMessage(f"Adding track: {s_name} ({src_app.name}:{s_id}) => {d_name} ({dst_app.name}:{d_id}) [manual]")
                            new_id_list.append(d_id)
                            self.parent.mapping_table.add('track', s_id, d_id)

                else:
                    cancel = True
                    break
                    
        if cancel:
            return
        
        print(f"Adding {len(new_id_list)} tracks to {dst_app.name} ...")
        if dst_app.add_saved_track(new_id_list):
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText(f"{len(new_id_list)} track(s) were added to {self.parent.dst_app.name}.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            
            self._loadTracks(dst_app, dst_model)

