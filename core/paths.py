"""
ACC Race Engineer — Path Helper
Resolves the base directory whether running as Python script or PyInstaller .exe
"""

import os
import sys


def get_base_dir() -> str:
    """Return the app's root directory.

    When running as a PyInstaller bundle, sys._MEIPASS points to the
    temp folder where files are extracted. Otherwise, use the normal
    project directory.
    """
    if getattr(sys, "_MEIPASS", None):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_path(filename: str = "cars.json") -> str:
    """Return full path to a file in the data/ folder."""
    return os.path.join(get_base_dir(), "data", filename)


def get_assets_path() -> str:
    """Return full path to the assets/ folder."""
    return os.path.join(get_base_dir(), "assets")


def get_exports_dir(subfolder: str = "") -> str:
    """Return path to the exports/ folder (or a subfolder). Created if missing.

    When bundled as .exe, this lives next to the .exe so users can find it.
    In dev mode, it lives in the project root.
    """
    if getattr(sys, "_MEIPASS", None):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exports = os.path.join(base, "exports")
    if subfolder:
        exports = os.path.join(exports, subfolder)
    os.makedirs(exports, exist_ok=True)
    return exports
