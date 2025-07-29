#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import QApplication

from main_window import MainWindow

from spotify_app import SpotifyApp
from tidal_app import TidalApp
  
# Create application
app = QApplication(sys.argv)

# Create main window
window = MainWindow()
window.set_src_app(SpotifyApp())
window.set_dst_app(TidalApp())

# Start the event loop.
app.exec()
