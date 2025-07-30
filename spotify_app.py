#!/usr/bin/env python3

import attridict
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from item_types import Artist, Album, Track, Playlist

################################################################################

class SpotifyApp:

    CLIENT_ID     = '4ff21dcb012a417ab5c1cb0574eb8983'
    CLIENT_SECRET = '9f82028d9eeb463695674ba7ac8429ef'

    REDIRECT_URI  = 'https://example.com/callback/'
    AUTH_SCOPE    = 'user-library-read,user-follow-read,user-follow-read'

    SESSION_FILE  = 'spotify-session-oauth.json'

    def __init__(self):

        self.auth = SpotifyOAuth(client_id=self.CLIENT_ID,
                                 client_secret=self.CLIENT_SECRET,
                                 redirect_uri=self.REDIRECT_URI,
                                 cache_path=self.SESSION_FILE,
                                 scope=self.AUTH_SCOPE,
                                 open_browser=False)

        self.sp = spotipy.Spotify(auth_manager=self.auth)

    @property
    def name(self):
        return 'Spotify'

    @property
    def uid(self):
        return self.sp.me()['id']

    def search_artist(self, name):
        result = self.sp.search(name, limit=10, type='artist')
        #print(result)
        items = [ attridict(r) for r in result['artists']['items'] ]
        return [ Artist( id=x.id, name=x.name)
                for x in items ]

    def search_album(self, name):
        result = self.sp.search(name, limit=10, type='album')
        #print(result)
        items = [ attridict(r) for r in result['albums']['items'] ]
        return [ Album( id=x.id, name=x.name,
                       artist=x.artists[0].name)
                for x in items ]

    def search_track(self, name):
        result = self.sp.search(name, limit=10, type='track')
        #print(result)
        items = [ attridict(r) for r in result['tracks']['items'] ]
        return [ Track( id=x.id, name=x.name,
                       artist=x.artists[0].name, album=x.album.name)
                for x in items ]

    def get_saved_artists(self):
        items = []
        after = None
        # accumulate data from multiple requests
        while True:
            result = self.sp.current_user_followed_artists(limit=50, after=after)
            #print(result)
            items.extend([ attridict(r) for r in result['artists']['items'] ])
            if result['artists']['next'] is None:
                break
            after = result['artists']['cursors']['after']
            assert after is not None

        return [ Artist(id=ar.id, name=ar.name)
                for ar in items ]

    def get_saved_albums(self):
        items = []
        offset = 0
        while True:
            result = self.sp.current_user_saved_albums(limit=50, offset=offset)
            #print(result)
            items.extend([ attridict(r) for r in result['items'] ])
            if result['next'] is None:
                break
            offset += 50

        return [ Album(id=al.album.id, name=al.album.name,
                       artist=al.album.artists[0].name)
                for al in items ]

    def get_saved_tracks(self):
        items = []
        offset = 0
        while True:
            result = self.sp.current_user_saved_tracks(limit=50, offset=offset)
            #print(result)
            items.extend([ attridict(r) for r in result['items'] ])
            if result['next'] is None:
                break
            offset += 50

        print(items[0])

        return [ Track(id=tr.track.id, name=tr.track.name,
                       artist=tr.track.artists[0].name, album=tr.track.album.name)
                for tr in items ]

    def get_playlists(self):
        items = []
        offset = 0
        while True:
            result = self.sp.current_user_playlists(limit=50, offset=offset)
            #print(result)
            items.extend([ attridict(r) for r in result['items'] ])
            if result['next'] is None:
                break
            offset += 50

        filled_items = []
        for pl in items:
            tracks = self.get_playlist_items(pl.id)
            filled_items.append(Playlist(id=pl.id, name=pl.name, descr=pl.description,
                                         tracks=tracks, public=pl.public))

        return filled_items

    def get_playlist_items(self, playlist_id: str):
        items = []
        offset = 0
        while True:
            result = self.sp.playlist_items(playlist_id, limit=50, offset=offset)
            #print(result)
            items.extend([ attridict(r) for r in result['items'] ])
            if result['next'] is None:
                break
            offset += 50

        return [ Track(id=tr.track.id, name=tr.track.name,
                       artist=tr.track.artists[0].name, album=tr.track.album.name)
                for tr in items ]


if __name__ == "__main__":
    api = SpotifyApp()

    print()
    print(api.get_saved_artists())

    print()
    print(api.get_saved_albums())

    print()
    print(api.get_saved_tracks())
