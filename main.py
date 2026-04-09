"""
ACC Race Engineer
A desktop tool for Assetto Corsa Competizione race strategy.

Features:
  - Fuel Calculator: estimate fuel needs, pit stops, and stint plans
  - Tire Advisor: find optimal tire pressures for weather conditions (Phase 2)

Requirements:
  pip install PyQt6

Usage:
  python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from core.car_data import CarDatabase
from ui.main_window import MainWindow
from ui.theme import DARK_RACING_THEME


def main():
    import os
    from core.paths import get_base_dir
    os.chdir(get_base_dir())

    app = QApplication(sys.argv)

    # Apply dark racing theme globally
    app.setStyleSheet(DARK_RACING_THEME)

    # Set default font
    font = QFont("Segoe UI", 13)
    app.setFont(font)

    # Load car database
    car_db = CarDatabase()

    # Launch main window
    window = MainWindow(car_db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
