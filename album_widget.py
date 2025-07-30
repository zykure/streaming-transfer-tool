from PyQt6.QtWidgets import *

from widget_template import _WidgetTemplate
from item_models import AlbumModel

#############################################################################

class AlbumWidget(_WidgetTemplate):
    def __init__(self, parent):
        super().__init__(parent)

        # album data
        self.wTableModelA = AlbumModel()
        self.wTableViewA.setModel(self.wTableModelA)

        self.wTableModelB = AlbumModel()
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

        self.parent.showMessage(f"\nLoading {app.name} albums ...")
        items = app.get_saved_albums()
        albums = sorted(items, key=lambda x: x.sortKey())

        print(f"=> Albums ({len(albums)}):")
        for album in albums:
            self.parent.showMessage(f"Loaded album: {album.name}")
            model.add(album)

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()

    def _transferData(self,
                      appA, viewA: QTableView,
                      appB, viewB: QTableView):

        modelA = viewA.model()
        modelB = viewB.model()

        for a_album in modelA.items:
            a_name = a_album.simplifiedName()
            a_id = a_album.id

            # Skip already added albums
            b_album = modelB.find(a_name)
            if b_album:
                b_id = str(b_album.id)
                self.parent.mappingTable.add('album', a_id, b_id)
                continue

            # Re-use known mapping
            b_id = self.parent.mappingTable.find('album', a_id)
            if b_id:
                b_album = appB.get_album(b_id)

                self.parent.showMessage(f"Transfer album: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [restored]")
                b_album.setDirty(True)  # mark as dirty to save later
                modelB.insert(b_album)
                continue

            # Search by album name
            query = f"{a_album.artist} - {a_album._name}"
            print("Searching for album:", query)
            result = appB.search_album(query)

            # Find matching album in search results
            match = False
            for b_album in result:
                b_name = b_album.simplifiedName()

                # Must have exact, case-insensitive match
                if b_album.name.lower() == a_album.name.lower() \
                        and b_album.artist.lower() == a_album.artist.lower():
                    b_id = str(b_album.id)

                    self.parent.showMessage(f"Transfer album: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [matched]")
                    b_album.setDirty(True)  # mark as dirty to save later
                    modelB.insert(b_album)
                    self.parent.mappingTable.add('album', a_id, b_id)

                    match = True
                    break

            if not match:
                # Allow to manually specify an album id
                dlg = QInputDialog(self)
                #dlg.setInputMode(QInputDialog.TextInput)
                dlg.setWindowTitle(f"Album not found on {appB.name}")
                dlg.setLabelText(f"Album NOT FOUND!\n{a_name}\n\nPlease provide id manually (leave empty to skip):")
                dlg.resize(400, 100)

                if dlg.exec():
                    # Get album by id
                    b_id = dlg.textValue().strip()
                    if b_id:
                        b_album = appB.get_album(b_id)
                        if b_album:
                            b_name = b_album.simplifiedName()

                            # Add saved album
                            self.parent.showMessage(f"Adding album: {a_name} ({appA.name}:{a_id}) => {b_name} ({appB.name}:{b_id}) [manual]")
                            b_album.setDirty(True)  # mark as dirty to save later
                            modelB.insert(b_album)
                            self.parent.mappingTable.add('album', a_id, b_id)

                else:
                    return

        self.wTableModelA.layoutChanged.emit()
        self.wTableModelB.layoutChanged.emit()

    def _submitData(self, app, view: QTableView):

        model = view.model()

        added_albums = []
        for item in model.items:
            if item.dirty:
                added_albums.append(item)

        if not added_albums:
            return

        print(added_albums)

        print(f"Adding {len(added_albums)} albums to {app.name} ...")
        app.add_saved_albums(added_albums)

        msg = QMessageBox(self)
        msg.setWindowTitle("Success")
        msg.setText(f"{len(added_albums)} album(s) were added to {app.name}.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        self._loadData(app, view)
