#!/usr/bin/env python3

from pathlib import Path
import urllib.parse
from typing import Callable
import tidalapi

from main_window import gMainWindow
from item_types import Artist, Album, Track, Playlist
from dialogs import MessageDialog, InputDialog

################################################################################

class GuiTidalSession(tidalapi.Session):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def login_pkce(self, fn_print: Callable[[str], None] = print) -> None:
        global gMainWindow
        
        # Get login url
        url_login: str = self.pkce_login_url()

        #fn_print("READ CAREFULLY!")
        #fn_print("---------------")
        #fn_print(
        #    "You need to open this link and login with your username and password. "
        #    "Afterwards you will be redirected to an 'Oops' page. "
        #    "To complete the login you must copy the URL from this 'Oops' page and paste it to the input field."
        #)
        #fn_print(url_login)
                            
        # Get redirect URL from user input.
        #url_redirect: str = input("Paste 'Ooops' page URL here and press <ENTER>:")
        
        url_login = 'https://example.com/test?param&param2'
        dlg = InputDialog(gMainWindow, f"{TidalApp.APP_NAME} login", 
            "You need to open this link and login with your username and password.<br/>"
            "Afterwards you will be redirected to an 'Oops' page.<br/><br/>"
            f'<a href="{url_login}">{url_login}</a><br/><br/>'
            "To complete the login you must copy the URL from this 'Oops' page and paste it to the input field.<br/>",
            hint="(Paste URL here)"
        )

        if dialog.exec():
            url_redirect: str = dlg.textValue()
        
        # Query for auth tokens
        json: dict[str, Union[str, int]] = self.pkce_get_auth_token(url_redirect)

        # Parse and set tokens.
        self.process_auth_token(json, is_pkce_token=True)

        # Swap the client_id and secret
        # self.client_enable_hires()
        
    def login_oauth_simple(self, fn_print: Callable[[str], None] = print) -> None:
        global gMainWindow
        
        login, future = self.login_oauth()
        #text = "Visit https://{0} to log in, the code will expire in {1} seconds."
        #fn_print(text.format(login.verification_uri_complete, login.expires_in))

        url_login, expires_in = login.verification_uri_complete, login.expires_in

        dlg = MessageDialog(gMainWindow, f"{TidalApp.APP_NAME} login", 
            f'Visit <a href="https://{url_login}">{url_login}</a> to log in.<br/>'
            f"The code will expire in {expires_in} seconds.<br/>"
        )
        dlg.exec()
        
        future.result()
      

################################################################################

class TidalApp:
    
    APP_NAME = 'Tidal'
    SESSION_FILE = 'tidal-session-oauth.json'

    def __init__(self):

        self.td = GuiTidalSession()
        self.td.login_session_file(Path(self.SESSION_FILE))

        self.user = self.td.user
        self.fav = tidalapi.Favorites(session=self.td, user_id=self.uid)

    @property
    def name(self):
        return self.APP_NAME

    @property
    def uid(self):
        return self.user.id

    @property
    def display_name(self):
        return f"{self.user.first_name or ''} {self.user.last_name or ''}"

    @staticmethod
    def get_search_url(query):
        q = urllib.parse.quote(query)
        url = f"https://tidal.com/search?q={q}"
        return url

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
        for item in self.user.playlists():
            if item.id == playlist.id:
                pl = item
                break
            if item.name == playlist.name:
                pl = item
                break

        # otherwise create new
        if not pl:
            pl = self.user.create_playlist(playlist.name, playlist.description)

        # clear playlist and add tracks
        pl.clear()
        pl.add([ tr.id for tr in playlist.getTracks() ], allow_duplicates=True)

        # update playlist details
        if playlist.public:
            pl.set_playlist_public()
        else:
            pl.set_playlist_private()

        return self.fav.add_playlist(pl.id)


if __name__ == "__main__":
    api = TidalApp()

    print(api.get_saved_artists())
    print(api.get_saved_albums())
    print(api.get_saved_tracks())
