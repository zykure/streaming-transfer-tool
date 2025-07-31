# Streaming Transfer Tool

This application provides a graphical user inteface to transfer content between music streaming services (e.g. saved artists, playlists, etc.) Some features are still under development.

Currently supported services:
* Spotify
* Tidal

The application is written in Python and uses PyQt6 for its GUI. See below for installation guides.

After downloading the sources, simply open a terminal and run:
```sh
python3 app.py
```

## Basic usage

The graphical interface allows you to transfer favorite artists, albums and tracks, and any playlists created by you.
(Shared playlists are not supported yet.)

The first time you run the app, you will need to authenticate with your personal account at the streaming two services. Authentication is cached on disk, so this is usually *not* necessary at every application start.

The tool allows to transfer saved artists etc. from one streaming platform to another.

The interface presents different tabs for artists, albums, tracks and playlists that each show the saved items for each platform as a table on the left and right side of the tab, with command buttons in the middle. The playlist tab shows two tables on each side, showing the user's playlists (top) and their tracks (bottom).

There are 3 buttons available:

* The **Load** buttons refresh the list on each side respectively. Green items are present on both platforms, orange ones are not.
* The **Transfer** buttons identify and transfer missing items (orange) from one platform to the other. The newly added items will be shown in yellow.
  * If items cannot be automatically identified on the target platform, a dialog asks you to manually look up and copy the corresponding item id (e.g. artist id). This can be easily retrieved from the URL when looking up the artist etc. in your browser.
  * You can leave the value empty to skip this item, or press Cancel to stop the transfer.
* The **Submit** buttons push the changes (yellow) to the respective platform. Artists, albums and tracks will be added to the user's favorite/saved lists, and playlists will be created/recreated with the contained tracks.

## Dependencies

You need a Python 3 installation on your system. The `pip` tool is required to install additional Python modules.

For help on installing Python on your system, see: 
https://realpython.com/installing-python/

Installation instructions for pip can be found here:
https://pip.pypa.io/en/stable/getting-started/

Required Python modules:

* attridict
* PyQt6
* spotipy
* tidalapi

Install command:
```sh
python3 -m pip install attridict pyqt6 spotipy tidalapi
```

## Development

The project is hosted on GitHub:

https://github.com/zykure/streaming-transfer-tool
