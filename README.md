# Streaming Transfer Tool

This application provides a graphical user inteface to transfer
content between music streaming services (e.g. saved artists,
playlists, etc.) Some features are still under development.

Currently supported services:
* Spotify
* Tidal

The application is written in Python and uses PyQt6 for its GUI.

Simply open a terminal and run:
```sh
python app.py
```
The graphical interface allows you to transfer favorite artists, 
albums and tracks, and any playlists created by you.
(Shared playlists are not supported yet.)

The first time you run the app, you will need to authenticate
with your personal account at the streaming two services.

## Dependencies

* attridict
* PyQt6
* spotipy
* tidalapi

Install command:
```sh
pip install attridict pyqt6 spotipy tidalapi
```

## Development

The project is hosted on GiHub:

https://github.com/zykure/streaming-transfer-tool
