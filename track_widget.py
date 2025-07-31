from PyQt6.QtWidgets import *

from widget_template import _WidgetTemplate
from dialogs import MessageDialog, InputDialog
from item_models import TrackModel

#############################################################################

class TrackWidget(_WidgetTemplate):
    def __init__(self, parent):
        super().__init__(parent)

        # track data
        self.wTableModelA = TrackModel()
        self.wTableViewA.setModel(self.wTableModelA)

        self.wTableModelB = TrackModel()
        self.wTableViewB.setModel(self.wTableModelB)

        self.wTableModelA.setSiblingModel(self.wTableModelB)
        self.wTableModelB.setSiblingModel(self.wTableModelA)

        # layout
        self.wLayout = QHBoxLayout()
        self.wLayout.addLayout(self.wLayoutA)
        self.wLayout.addLayout(self.wButtonLayout)
        self.wLayout.addLayout(self.wLayoutB)

        self.setLayout(self.wLayout)

    def _loadData(self, app, view: QTableView):

        model = view.model()
        model.clear()
        
        self.parent.busy()
        self.parent.showMessage(f"\nLoading {app.name} tracks ...")
        
        items = app.get_saved_tracks()
        tracks = sorted(items, key=lambda x: x.sortKey())

        print(f"=> Tracks ({len(tracks)}):")
        for track in tracks:
            self.parent.showMessage(f"Loaded track: {track.name}")
            model.add(track)

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()

        self.parent.showMessage(f"\nLoaded {len(model.items)} tracks from {app.name} ...")
        self.parent.done()

    def _transferData(self,
                      appA, viewA: QTableView,
                      appB, viewB: QTableView):

        modelA = viewA.model()
        modelB = viewB.model()
        
        self.parent.busy()

        num_items = 0

        for a_track in modelA.items:
            a_name = a_track.simplifiedName()
            a_id = a_track.id

            # Skip already added track
            b_track = modelB.find(a_name)
            if b_track:
                b_id = str(b_track.id)
                self.parent.mappingTable.add('track', a_id, b_id)
                continue

            # Re-use known mapping
            b_id = self.parent.mappingTable.find('track', a_id)
            if b_id:
                b_track = appB.get_track(b_id)
                b_name = b_track.simplifiedName()

                self.parent.showMessage(f"Transfer track: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [restored]")
                b_track.setDirty(True)  # mark as dirty to save later
                modelB.insert(b_track)
                num_items += 1
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
                b_name = b_track.simplifiedName()

                # Must have exact, case-insensitive match
                if b_track.name.lower() == a_track.name.lower() \
                        and b_track.artist.lower() == a_track.artist.lower() \
                        and b_track.album.lower() == a_track.album.lower():
                    b_id = str(b_track.id)

                    self.parent.showMessage(f"Transfer track: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [matched]")
                    b_track.setDirty(True)  # mark as dirty to save later
                    modelB.insert(b_track)
                    num_items += 1
                    self.parent.mappingTable.add('track', a_id, b_id)

                    match = True
                    break

            if not match:
                # Allow to manually specify an track id
                search_url = appB.get_search_url(query)
                dlg = InputDialog(self, f"Track not found on {appB.name}",
                    "Track NOT FOUND!<br/>"
                    f'<a href="{search_url}">{a_name}</a><br/><br/>'
                    "Please provide id manually (leave empty to skip):<br/>",
                    hint="(Paste Track id here)"
                )
                dlg.resize(400, 100)
                
                if dlg.exec():
                    # Get track by id
                    b_id = dlg.textValue().strip()
                    if b_id:
                        b_track = appB.get_track(b_id)
                        if b_track:
                            b_name = b_track.simplifiedName()

                            # Add saved track
                            self.parent.showMessage(f"Adding track: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [manual]")
                            b_track.setDirty(True)  # mark as dirty to save later
                            modelB.insert(b_track)
                            num_items += 1
                            self.parent.mappingTable.add('track', a_id, b_id)

                else:
                    return

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()

        self.parent.showMessage(f"\nTransferred {num_items} albums to {appB.name} ...")
        self.parent.done()
        
    def _submitData(self, app, view: QTableView):

        model = view.model()

        added_tracks = []
        for item in model.items:
            if item.dirty:
                added_tracks.append(item)

        if not added_tracks:
            self.parent.showMessage(f"\nThere are no tracks to be sumitted to {app.name} ...")
            return
            
        self.parent.busy()

        #print(added_tracks)
        print(f"Adding {len(added_tracks)} tracks to {app.name} ...")
        app.add_saved_tracks(added_tracks)

        dlg = MessageDialog(self, "Success!",
            f"{len(added_tracks)} track(s) were added to {app.name}.")
        dlg.exec()

        self._loadData(app, view)

        self.parent.showMessage(f"\nSubmtited {len(added_tracks)} tracks to {app.name} ...")
        self.parent.done()
        