from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import *

from widget_template import _WidgetTemplate
from dialogs import MessageDialog, InputDialog
from item_models import PlaylistModel, TrackModel
from item_types import Playlist

#############################################################################

class PlaylistWidget(_WidgetTemplate):
    def __init__(self, parent):
        super().__init__(parent)

        # playlist data
        self.wTableModelA = PlaylistModel()
        self.wTableViewA.setModel(self.wTableModelA)

        self.wTableModelB = PlaylistModel()
        self.wTableViewB.setModel(self.wTableModelB)

        self.wTableModelA.setSiblingModel(self.wTableModelB)
        self.wTableModelB.setSiblingModel(self.wTableModelA)

        # track data
        self.wTableTracksModelA = TrackModel()
        self.wTableTracksViewA = QTableView()
        self.wTableTracksViewA.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableTracksViewA.verticalHeader().hide()
        self.wTableTracksViewA.setModel(self.wTableTracksModelA)
        self.wTableTracksViewA.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.wTableTracksModelB = TrackModel()
        self.wTableTracksViewB = QTableView()
        self.wTableTracksViewB.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.wTableTracksViewB.verticalHeader().hide()
        self.wTableTracksViewB.setModel(self.wTableTracksModelB)
        self.wTableTracksViewB.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.wTableTracksModelA.setSiblingModel(self.wTableTracksModelB)
        self.wTableTracksModelB.setSiblingModel(self.wTableTracksModelA)

        # signals
        self.wTableViewA.selectionModel().selectionChanged.connect(self.selectTableA)
        self.wTableViewB.selectionModel().selectionChanged.connect(self.selectTableB)

        self.wTableTracksViewA.verticalScrollBar().valueChanged.connect(self.scrollTracksTableA)
        self.wTableTracksViewB.verticalScrollBar().valueChanged.connect(self.scrollTracksTableB)

        # layout
        self.wLayoutA = QVBoxLayout()
        self.wLayoutA.addWidget(self.wLabelA)
        self.wLayoutA.addWidget(self.wTableViewA)
        self.wLayoutA.addWidget(self.wTableTracksViewA)

        self.wLayoutB = QVBoxLayout()
        self.wLayoutB.addWidget(self.wLabelB)
        self.wLayoutB.addWidget(self.wTableViewB)
        self.wLayoutB.addWidget(self.wTableTracksViewB)

        self.wLayout = QHBoxLayout()
        self.wLayout.addLayout(self.wLayoutA)
        self.wLayout.addLayout(self.wButtonLayout)
        self.wLayout.addLayout(self.wLayoutB)

        self.setLayout(self.wLayout)  # override default layout

    def selectTableA(self, selected, deselected):
        if selected.indexes():
            rowIndex = selected.indexes()[0].row()
            playlist = self.wTableModelA.items[rowIndex]

            self.wTableTracksModelA.clear()
            for track in playlist.getTracks():
                self.wTableTracksModelA.add(track)

            self.wTableTracksModelA.layoutChanged.emit()

    def selectTableB(self, selected, deselected):
       if selected.indexes():
            rowIndex = selected.indexes()[0].row()
            playlist = self.wTableModelB.items[rowIndex]

            self.wTableTracksModelB.clear()
            for track in playlist.getTracks():
                self.wTableTracksModelB.add(track)

            self.wTableTracksModelB.layoutChanged.emit()

    def scrollTracksTableA(self):
        """Synchronize B with A scroll bar."""

        self._scrollTable(self.wTableTracksViewA, self.wTableTracksViewB)

    def scrollTracksTableB(self):
        """Synchronize A with B scroll bar."""

        self._scrollTable(self.wTableTracksViewB, self.wTableTracksViewA)

    def _loadData(self, app, view: QTableView):

        model = view.model()
        model.clear()

        self.parent.busy()
        print(f"\nLoading {app.name} playlists ...")
        
        items = app.get_playlists()
        playlists = sorted(items, key=lambda x: x.sortKey())

        num_tracks = 0
        print(f"=> Playlist ({len(playlists)}):")
        for playlist in playlists:
            print(f"Loaded playlist: {playlist.name}")
            model.add(playlist)
            num_tracks += playlist.numTracks()

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()
        self.wTableTracksModelA.layoutChanged.emit()
        self.wTableTracksModelB.layoutChanged.emit()

        self.parent.showMessage(f"\nLoaded {len(model.items)} playlists with {num_tracks} tracks from {app.name} ...")
        self.parent.done()

    def _transferData(self,
                      appA, viewA: QTableView,
                      appB, viewB: QTableView):

        modelA = viewA.model()
        modelB = viewB.model()

        input_playlists = []
        if viewA.selectedIndexes():
            for index in viewA.selectedIndexes():
                rowIndex = index.row()
                playlist = modelA.items[rowIndex]

            input_playlists.append(playlist)

        else:
            #input_playlists = modelA.items
            self.parent.showMessage("Select a playlist entry first!")
            return
            
        self.parent.busy()

        num_items = 0
        num_tracks = 0

        for a_playlist in input_playlists:
            a_name = a_playlist.simplifiedName()
            a_id = a_playlist.id

            # # Skip already added playlist
            # b_playlist = modelB.find(a_name)
            # if b_playlist:
            #     b_id = str(b_playlist.id)
            #     self.parent.mappingTable.add('playlist', a_id, b_id)
            #     continue

            # print(f"Transfer playlist: {a_name} ({appA.name}:{a_id})")

            b_playlist = modelB.find(a_name)
            if not b_playlist:
                b_playlist = Playlist("", name=a_name, descr=a_playlist.description,
                                      tracks=[], public=a_playlist.public)
                modelB.insert(b_playlist)

            b_playlist.clearTracks()  # clear playlist to ensure correct track order when adding
            b_playlist.setDirty(True)  # mark as dirty to save later
            num_items += 1

            # Process playlist's tracks

            for a_track in a_playlist.getTracks():
                a_track_name = a_track.simplifiedName()
                a_track_id = a_track.id

                # Skip already added track
                b_track = modelB.find(a_track_name)
                if b_track:
                    b_track_id = str(b_track.id)
                    b_playlist.addTrack(b_track)
                    self.parent.mappingTable.add('track', a_track_id, b_track_id)
                    continue

                # Re-use known mapping
                b_track_id = self.parent.mappingTable.find('track', a_track_id)
                if b_track_id:
                    b_track = appB.get_track(b_track_id)
                    b_track_name = b_track.simplifiedName()

                    print(f"Transfer track: {a_track_name} ({appA.name}:{a_track_id}) => {b_track_name} ({appB.name}:{b_track_id}) [restored]")
                    b_playlist.addTrack(b_track)
                    num_tracks += 1
                    continue

                # Search by track name
                query = f"{a_track.artist} - {a_track.album} - {a_track._name}"
                print("Searching for track:", query)
                result = appB.search_track(query)
                if not result:
                    # Redo search without album name
                    query = f"{a_track.artist} - {a_track._name}"
                    print("Searching for track:", query)
                    result = appB.search_track(query)

                # Find matching track in search results
                match = False
                for b_track in result:
                    b_track_name = b_track.simplifiedName()

                    # Must have exact, case-insensitive match
                    if b_track.name.lower() == a_track.name.lower() \
                            and b_track.artist.lower() == a_track.artist.lower() \
                            and b_track.album.lower() == a_track.album.lower():
                        b_track_id = str(b_track.id)

                        print(f"Transfer track: {a_name} ({appA.name}:{a_track_id}) => {b_track_name} ({appB.name}:{b_track_id}) [matched]")
                        b_playlist.addTrack(b_track)
                        num_tracks += 1
                        self.parent.mappingTable.add('track', a_track_id, b_track_id)

                        match = True
                        break

                if not match:
                    # Allow to manually specify an track id
                    search_url = appB.get_search_url(query)
                    dlg = InputDialog(self, f"Track not found on {appB.name}",
                        "Track NOT FOUND!<br/>"
                        f'<a href="{search_url}">{a_track_name}</a><br/><br/>'
                        "Please provide id manually (leave empty to skip):<br/>",
                        hint="(Paste Track id here)"
                    )
                    dlg.resize(400, 100)

                    if dlg.exec():
                        # Get track by id
                        b_track_id = dlg.textValue().strip()
                        if b_track_id:
                            b_track = appB.get_track(b_track_id)
                            if b_track:
                                b_track_name = b_track.simplifiedName()

                                # Add saved track
                                print(f"Adding track: {a_track_name} ({appA.name}:{a_track_id}) => {b_track_name} ({appB.name}:{b_track_id}) [manual]")
                                b_playlist.addTrack(b_track)
                                num_tracks += 1
                                self.parent.mappingTable.add('track', a_track_id, b_track_id)

                    else:
                        return

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()
        self.wTableTracksModelA.layoutChanged.emit()
        self.wTableTracksModelB.layoutChanged.emit()

        if not viewB.selectedIndexes():
            if len(modelB.items) > 0:
                viewB.selectRow(0)

        self.parent.showMessage(f"\nTransferred {num_items} playlists with {num_tracks} tracks to {appB.name} ...")
        self.parent.done()
        
    def _submitData(self, app, view: QTableView):

        model = view.model()

        added_playlists = []
        num_tracks = 0
        for playlist in model.items:
            if playlist.dirty:
                added_playlists.append(playlist)
                num_tracks += playlist.numTracks()

        if not added_playlists:
            self.parent.showMessage(f"\nThere are no playlists to be sumitted to {app.name} ...")
            return

        self.parent.busy()

        #print(added_playlists)
        print(f"Adding {len(added_playlists)} playlists to {app.name} ...")
        for playlist in added_playlists:
            app.add_playlist(playlist)

        dlg = MessageDialog(self, "Success!",
            f"{len(added_playlists)} playlist(s) with {num_tracks} track(s) were added to {app.name}.")
        dlg.exec() 
        
        self._loadData(app, view)

        self.parent.showMessage(f"\nSubmitted {len(added_playlists)} playlists with {num_tracks} tracks to {app.name} ...")
        self.parent.done()
        