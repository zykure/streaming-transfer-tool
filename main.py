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
window.setSrcApp(SpotifyApp())
window.setDstApp(TidalApp())

# Start the event loop.
app.exec()
