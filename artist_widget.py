from PyQt6.QtWidgets import *

from widget_template import _WidgetTemplate
from dialogs import MessageDialog, InputDialog
from item_models import ArtistModel

#############################################################################

class ArtistWidget(_WidgetTemplate):
    def __init__(self, parent):
        super().__init__(parent)

        # artist data
        self.wTableModelA = ArtistModel()
        self.wTableViewA.setModel(self.wTableModelA)

        self.wTableModelB = ArtistModel()
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
        print(f"\nLoading artists from {app.name} ...")
        
        items = app.get_saved_artists()
        artists = sorted(items, key=lambda x: x.sortKey())

        print(f"=> Artists ({len(artists)}):")
        for artist in artists:
            print(f"Loaded artist: {artist.name}")
            model.add(artist)

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()
        
        self.parent.showMessage(f"\nLoaded {len(model.items)} artists from {app.name} ...")
        self.parent.done()

    def _transferData(self,
                      appA, viewA: QTableView,
                      appB, viewB: QTableView):

        modelA = viewA.model()
        modelB = viewB.model()
                
        self.parent.busy()

        num_items = 0

        for a_artist in modelA.items:
            a_name = a_artist.simplifiedName()
            a_id = a_artist.id

            # Skip already added artists
            b_artist = modelB.find(a_name)
            if b_artist:
                b_id = str(b_artist.id)
                self.parent.mappingTable.add('artist', a_id, b_id)
                continue

            # Re-use known mapping
            b_id = self.parent.mappingTable.find('artist', a_id)
            if b_id:
                b_artist = appB.get_artist(b_id)

                print(f"Transfer artist: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [restored]")
                b_artist.setDirty(True)  # mark as dirty to save later
                modelB.insert(b_artist)
                num_items += 1
                continue

            # Search by artist name
            query = a_artist._name
            print("Searching for artist:", query)
            result = appB.search_artist(query)

            # Find matching artist in search results
            match = False
            for b_artist in result:
                b_name = b_artist.simplifiedName()

                # Must have exact, case-insensitive match
                if b_artist.name.lower() == a_artist.name.lower():
                    b_id = str(b_artist.id)

                    print(f"Transfer artist: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [matched]")
                    b_artist.setDirty(True)  # mark as dirty to save later
                    modelB.insert(b_artist)
                    num_items += 1
                    self.parent.mappingTable.add('artist', a_id, b_id)

                    match = True
                    break

            if not match:
                # Allow to manually specify an artist id
                search_url = appB.get_search_url(query)
                dlg = InputDialog(self, f"Artist not found on {appB.name}",
                    "Artist NOT FOUND!<br/>"
                    f'<a href="{search_url}">{a_name}</a><br/><br/>'
                    "Please provide id manually (leave empty to skip):<br/>",
                    hint="(Paste Artist id here)"
                )
                dlg.resize(400, 100)

                if dlg.exec():
                    # Get artist by id
                    b_id = dlg.textValue().strip()
                    if b_id:
                        b_artist = appB.get_artist(b_id)
                        if b_artist:
                            b_name = b_artist.simplifiedName()

                            # Add saved artist
                            print(f"Adding artist: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [manual]")
                            b_artist.setDirty(True)  # mark as dirty to save later
                            modelB.insert(b_artist)
                            num_items += 1
                            self.parent.mappingTable.add('artist', a_id, b_id)

                else:
                    return

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()

        self.parent.showMessage(f"\nTransferred {num_items} artists to {appB.name} ...")
        self.parent.done()

    def _submitData(self, app, view: QTableView):

        model = view.model()

        added_artists = []
        for item in model.items:
            if item.dirty:
                added_artists.append(item)

        if not added_artists:
            self.parent.showMessage(f"\nThere are no artists to be sumitted to {app.name} ...")
            return
        
        self.parent.busy()

        #print(added_artists)
        print(f"Adding {len(added_artists)} artists to {app.name} ...")
        app.add_saved_artists(added_artists)

        dlg = MessageDialog(self, "Success!",
            f"{len(added_artists)} artist(s) were added to {app.name}.")
        dlg.exec()
        
        self._loadData(app, view)
        
        self.parent.showMessage(f"\nSubmitted {len(added_artists)} artists to {app.name} ...")
        self.parent.done()
