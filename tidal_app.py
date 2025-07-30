#!/usr/bin/env python3

import tidalapi
from pathlib import Path

from item_types import Artist, Album, Track, Playlist

################################################################################

class TidalApp:

    SESSION_FILE = 'tidal-session-oauth.json'

    def __init__(self):

        self.td = tidalapi.Session()
        self.td.login_session_file(Path(self.SESSION_FILE))

        self.user = self.td.user
        self.fav = tidalapi.Favorites(session=self.td, user_id=self.uid)

    @property
    def name(self):
        return 'Tidal'

    @property
    def uid(self):
        return self.user.id

    def search_artist(self, name):
        result = self.td.search(name, limit=10, models=[tidalapi.Artist])
        #print(result)
        items = result['artists']
        return [ Artist(id=ar.id, name=ar.name)
                for ar in items]

    def search_album(self, name):
        result = self.td.search(name, limit=10, models=[tidalapi.Album])
        #print(result)
        items = result['albums']
        return [ Album(id=al.id, name=al.name,
                       artist=al.artists[0].name)
                for al in items]

    def search_track(self, name):
        result = self.td.search(name, limit=10, models=[tidalapi.Track])
        #print(result)
        items = result['tracks']
        return [ Track(id=tr.id, name=tr.name,
                       artist=tr.artists[0].name, album=tr.album.name)
                for tr in items]

    def get_artist(self, id):
        result = self.td.artist(id)
        return Artist(id=result.id, name=result.name)

    def get_album(self, id):
        result = self.td.album(id)
        return Album(id=result.id, name=result.name,
                     artist=result.artists[0].name)

    def get_track(self, id):
        result = self.td.track(id)
        return Track(id=result.id, name=result.name,
                     artist=result.artists[0].name, album=result.album.name)

    def get_saved_artists(self):
        result = self.fav.artists()
        #print(result)
        return [ Artist(id=ar.id, name=ar.name)
                for ar in result ]

    def get_saved_albums(self):
        result = self.fav.albums()
        #print(result)
        return [ Album(id=al.id, name=al.name,
                       artist=al.artists[0].name)
                for al in result ]

    def get_saved_tracks(self):
        result = self.fav.tracks()
        #print(result)
        return [ Track(id=tr.id, name=tr.name,
                       artist=tr.artists[0].name, album=tr.album.name)
                for tr in result ]

    def get_playlists(self):
        result = self.user.playlists()
        #print(result)
        return [ Playlist(id=pl.id, name=pl.name, descr=pl.description,
                          tracks=[ Track(id=tr.id, name=tr.name,
                                         artist=tr.artists[0].name, album=tr.album.name)
                                  for tr in pl.tracks() ],
                          public=pl.public)
                 for pl in result ]

    def add_saved_artists(self, artists: list[Artist]):
        return self.fav.add_artist([ ar.id for ar in artists ])

    def add_saved_albums(self, albums: list[Album]):
        return self.fav.add_album([ al.id for al in albums ])

    def add_saved_tracks(self, tracks: list[Track]):
        return self.fav.add_track([ tr.id for tr in tracks ])

    def add_playlist(self, playlist: Playlist):
        # first try to find existing playlist
        pl = None
        for pl in self.user.playlists():
            if pl.name == playlist.name:
                break

        # otherwise create new
        if not pl:
            pl = self.user.create_playlist(playlist.name, playlist.description)

        # clear playlist and add tracks
        pl.clear()
        pl.add([ tr.id for tr in playlist.getTracks() ], allow_duplicates=False)

        # update playlist details
        if playlist.public:
            pl.set_playlist_public()
        else:
            pl.set_playlist_private()

        return self.fav.add_playlist(pl.id)


if __name__ == "__main__":
    api = TidalApp()

    #api.get_saved_artists()
    #api.get_saved_albums()
    #api.get_saved_tracks()
    api.get_playlists()
