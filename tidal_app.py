#!/usr/bin/env python3

import tidalapi
from pathlib import Path

################################################################################

class TidalApp:

    SESSION_FILE = 'tidal-session-oauth.json'

    def __init__(self):
        
        self.td = tidalapi.Session()
        self.td.login_session_file(Path(self.SESSION_FILE))

        self.fav = tidalapi.Favorites(session=self.td, user_id=self.uid)

    @property
    def name(self):
        return 'Tidal'

    @property
    def uid(self):
        return self.td.user.id

    def search_artist(self, name):
        result = self.td.search(name, limit=10, models=[tidalapi.Artist])
        #print(result)
        return result['artists']

    def search_album(self, name):
        result = self.td.search(name, limit=10, models=[tidalapi.Album])
        #print(result)
        return result['albums']

    def search_track(self, name):
        result = self.td.search(name, limit=10, models=[tidalapi.Track])
        #print(result)
        return result['tracks']

    def get_artist(self, id):
        return self.td.artist(id)

    def get_album(self, id):
        return self.td.album(id)

    def get_track(self, id):
        return self.td.track(id)

    def get_saved_artists(self):
        result = self.fav.artists()
        #print(result)
        return result

    def get_saved_albums(self):
        result = self.fav.albums()
        #print(result)
        return result

    def get_saved_tracks(self):
        result = self.fav.tracks()
        #print(result)
        return result

    def get_playlists(self):
        result = self.fav.playlists()
        #print(result)
        return result

    def add_saved_artist(self, id):
        return self.fav.add_artist(id)

    def add_saved_album(self, id):
        return self.fav.add_album(id)

    def add_saved_track(self, id):
        return self.fav.add_track(id)


if __name__ == "__main__":
    api = TidalApp()

    api.get_saved_artists()
    api.get_saved_albums()
    api.get_saved_tracks()
