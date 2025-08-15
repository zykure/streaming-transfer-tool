#!/usr/bin/env python3

import attridict
import html
import json
import urllib.parse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from main_window import gMainWindow
from item_types import Artist, Album, Track, Playlist
from dialogs import InputDialog

################################################################################

class GuiSpotifyOAuth(SpotifyOAuth):
    def __init__( self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def _get_auth_response_interactive(self, open_browser=False):
        global gMainWindow
        
        #if open_browser:
        #    self._open_auth_url()
        #    prompt = "Enter the URL you were redirected to: "
        #else:
        #    url = self.get_authorize_url()
        #    prompt = (
        #        f"Go to the following URL: {url}\n"
        #        "Enter the URL you were redirected to: "
        #    )
        #response = self._get_user_input(prompt)
        
        url = self.get_authorize_url()
        dlg = InputDialog(gMainWindow, f"{SpotifyApp.APP_NAME} login", 
            "Go to the following URL:<br/>"
            f'<a href="{url}">{url}</a><br/><br/>'
            "Enter the URL you were redirected to:<br/>",
            hint="(Paste URL here)"
        )

        if dlg.exec():
            response: str = dlg.textValue()
            #print(response)
            state, code = SpotifyOAuth.parse_auth_response_url(response)
            
            if self.state is not None and self.state != state:
                raise SpotifyStateError(self.state, state)
            return code

################################################################################

class SpotifyApp:

    REDIRECT_URI  = 'https://example.com/callback/'
    AUTH_SCOPE    = ','.join([
            'playlist-read-private',
            'playlist-modify-private',
            'playlist-modify-public',
            'user-follow-read',
            'user-follow-modify',
            'user-library-read',
            'user-library-modify',
        ])

    APP_NAME = 'Spotify'
    SESSION_FILE  = 'spotify-session-oauth.json'
    CLIENT_FILE = 'spotify-api-client.json'
       
    def __init__(self):
        
        self.auth = None
        self.sp = None
        
        self.client_id: str = ""
        self.client_secret: str = ""
        
        self.restore_client()

    def connect(self):
        global gMainWindow

        # get client_id if not defined
        if not self.client_id:
            dlg = InputDialog(gMainWindow, f"{SpotifyApp.APP_NAME} API", 
                "Please enter a valid <b>CLIENT ID</b> for the Spotify API:<br/>",
                hint="(Paste ID here)"
            )
            
            if dlg.exec():
                self.client_id = dlg.textValue()

        # get client_secret if not defined
        if not self.client_secret:
            dlg = InputDialog(gMainWindow, f"{SpotifyApp.APP_NAME} API", 
                "Please enter a valid <b>CLIENT SECRET</b> for the Spotify API:<br/>",
                hint="(Paste SECRET here)"
            )
  
            if dlg.exec():
                self.client_secret = dlg.textValue()
           
        self.auth = GuiSpotifyOAuth(client_id=self.client_id,
                                    client_secret=self.client_secret,
                                    redirect_uri=self.REDIRECT_URI,
                                    cache_path=self.SESSION_FILE,
                                    scope=self.AUTH_SCOPE)

        self.sp = spotipy.Spotify(auth_manager=self.auth)
                
        self.store_client()

    def restore_client(self):
        
        try:
            with open(self.CLIENT_FILE, 'r') as f:
                data = json.load(f)
                self.client_id = data.get('client_id', "")
                self.client_secret = data.get('client_secret', "")
        except FileNotFoundError as e:
            return
           
    def store_client(self):

        with open(self.CLIENT_FILE, 'w') as f:
            json.dump({
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }, f)
         
    @property
    def name(self):
        return self.APP_NAME

    @property
    def uid(self):
        return self.sp.me()['id']

    @property
    def display_name(self):
        return self.sp.me()['display_name']

    @staticmethod
    def get_search_url(query):
        q = urllib.parse.quote(query)
        url = f"https://open.spotify.com/search/{q}"
        return url

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

            filled_items.append(Playlist(id=pl.id, 
                                         name=pl.name, 
                                         descr=html.unescape(pl.description),
                                         tracks=tracks, 
                                         public=pl.public, 
                                         image_url=pl.images[0]['url'] if pl.images else ""))

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

    def add_saved_artists(self, artists: list[Artist]):
        return self.sp.user_follow_artists([ ar.id for ar in artists ])

    def add_saved_albums(self, albums: list[Album]):
        return self.sp.current_user_saved_albums_add([ al.id for al in albums ])

    def add_saved_tracks(self, tracks: list[Track]):
        return self.sp.current_user_saved_tracks_add([ tr.id for tr in tracks ])
        
    def add_playlist(self, playlist: Playlist):
        # first try to find existing playlist
        pl_id = None

        offset = 0
        while pl_id is None:
            result = self.sp.current_user_playlists(limit=50, offset=offset)
            #print(result)
            for item in result['items']:
                if item['id'] == playlist.id:
                    pl_id = item['id']
                    break
                if item['name'] == playlist.name:
                    pl_id = item['id']
                    break                
            if result['next'] is None:
                break
            offset += 50            
        
        # otherwise create new
        if not pl_id:
            pl_id = self.sp.user_playlist_create(self.uid, playlist.name)
        
        for tracks in playlist.getTracks(chunk_size=50):
            self.sp.playlist_replace_items(pl_id, [ tr.id for tr in tracks ])
        
        self.sp.playlist_change_details(pl_id, 
            public=playlist.public, description=html.escape(playlist.description))
            
        return pl_id

if __name__ == "__main__":
    api = SpotifyApp()

    print(api.get_saved_artists())
    print(api.get_saved_albums())
    print(api.get_saved_tracks())
