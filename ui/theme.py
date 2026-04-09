"""
ACC Race Engineer — Dark Racing Theme
QSS stylesheet for a professional, racing-inspired dark UI.
"""

import os as _os
import sys as _sys
import shutil as _shutil
import tempfile as _tempfile

# Copy arrow icons to a temp dir with no spaces (Qt QSS url() chokes on spaces)
# Use PyInstaller's _MEIPASS if running as bundled .exe
if getattr(_sys, "_MEIPASS", None):
    _SRC_ASSETS = _os.path.join(_sys._MEIPASS, "assets")
else:
    _SRC_ASSETS = _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        "assets",
    )

_TEMP_ASSETS = _os.path.join(_tempfile.gettempdir(), "acc_engineer_assets")
_os.makedirs(_TEMP_ASSETS, exist_ok=True)

for _f in _os.listdir(_SRC_ASSETS):
    _src = _os.path.join(_SRC_ASSETS, _f)
    _dst = _os.path.join(_TEMP_ASSETS, _f)
    if _os.path.isfile(_src):
        _shutil.copy2(_src, _dst)

_ASSETS = _TEMP_ASSETS.replace("\\", "/")

_DARK_RACING_THEME = """
/* ===== GLOBAL ===== */

/* Default style for every widget in the app */
QWidget {
    background-color: #0D0F14;
    color: #E0E4EC;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* The main application window background */
QMainWindow {
    background-color: #0D0F14;
}

/* ===== TAB WIDGET ===== */

/* The tab container that holds Fuel Calculator and Tire Advisor */
QTabWidget {
    border: none;
}

/* The content area below the tab buttons */
QTabWidget::pane {
    border: none;
    background-color: #12151C;
    top: 0px;
}

/* The row that holds the tab buttons */
QTabWidget::tab-bar {
    border: none;
}

/* The tab bar itself — drawBase: 0 removes the white line under tabs */
QTabBar {
    background-color: #0D0F14;
    border: none;
    qproperty-drawBase: 0;
}

/* Each individual tab button (e.g. "FUEL CALCULATOR", "TIRE ADVISOR") */
QTabBar::tab {
    background-color: #161A24;
    color: #8891A5;
    border: none;
    padding: 10px 28px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.5px;
    min-width: 140px;
}

/* The currently active/selected tab — red text with red underline */
QTabBar::tab:selected {
    background-color: #12151C;
    color: #FF4A3D;
    border: none;
    border-bottom: 2px solid #FF4A3D;
}

/* Tab button when hovered but not selected */
QTabBar::tab:hover:!selected {
    background-color: #1A1F2B;
    color: #C0C7D6;
}

/* ===== GROUP BOX ===== */

/* Sections like "CAR SELECTION", "RACE PARAMETERS", "FUEL DATA" */
QGroupBox {
    background-color: #12151C;
    border: 1px solid #1E2330;
    border-radius: 8px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-weight: 700;
    font-size: 13px;
    color: #FF4A3D;
}

/* The section title label (e.g. "CAR SELECTION") */
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background-color: #161A24;
    border: 1px solid #1E2330;
    border-radius: 4px;
    left: 12px;
}

/* ===== LABELS ===== */

/* Default text label (e.g. "Class", "Car", "Tank Capacity") */
QLabel {
    color: #B0B8C8;
    background-color: transparent;
    font-size: 13px;
}

/* Section headings like "FUEL STRATEGY RESULTS" */
QLabel[class="heading"] {
    color: #FF4A3D;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
}

/* Big result numbers in white (e.g. laps per tank value) */
QLabel[class="value-large"] {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 700;
}

/* Big result numbers in red (e.g. total fuel, pit stops) */
QLabel[class="value-accent"] {
    color: #FF4A3D;
    font-size: 28px;
    font-weight: 700;
}

/* Small unit text below result values (e.g. "LITERS", "LAPS", "STOPS") */
QLabel[class="unit"] {
    color: #5A6275;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Small header text above result values (e.g. "TOTAL FUEL NEEDED") */
QLabel[class="result-label"] {
    color: #8891A5;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
}

/* ===== COMBO BOX ===== */

/* The whole dropdown box (Class, Car, Race Mode, etc.) */
QComboBox {
    background-color: #161A24;
    border: 1px solid #2A3040;
    border-radius: 6px;
    padding: 8px 12px;
    color: #E0E4EC;
    font-size: 13px;
    min-height: 20px;
}

/* When you hover the mouse over the dropdown box */
QComboBox:hover {
    border-color: #FF4A3D;
    background-color: #1A1F2B;
}

/* When the dropdown box is clicked/focused */
QComboBox:focus {
    border-color: #FF4A3D;
    background-color: #1A1F2B;
    outline: none;
}

/* The clickable button area on the right side that opens the list */
QComboBox::drop-down {
    border: none;
    width: 30px;
    background-color: transparent;
}

/* The small chevron arrow icon inside the drop-down button */
QComboBox::down-arrow {
    image: url(%%ASSETS%%/arrow-down.png);
    width: 10px;
    height: 7px;
    margin-right: 10px;
}

/* The popup list that appears when you click the dropdown */
QComboBox QAbstractItemView {
    background-color: #161A24;
    border: 1px solid #FF4A3D;
    border-radius: 4px;
    selection-background-color: #FF4A3D;
    selection-color: #FFFFFF;
    color: #E0E4EC;
    padding: 4px;
    margin-top: 2px;
}

/* ===== SPIN BOX / DOUBLE SPIN BOX ===== */
/* Number inputs — QSpinBox for whole numbers (laps), QDoubleSpinBox for decimals (fuel) */

/* The whole number input box */
QSpinBox, QDoubleSpinBox {
    background-color: #161A24;
    border: 1px solid #2A3040;
    border-radius: 6px;
    padding: 8px 12px;
    color: #E0E4EC;
    font-size: 14px;
    font-weight: 600;
    min-height: 20px;
}

/* When you hover the mouse over the number input */
QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #FF4A3D;
}

/* When the number input is clicked/focused */
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #FF4A3D;
}

/* The top half button on the right side (increase value) */
QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #1E2330;
    border: none;
    border-top-right-radius: 5px;
    width: 28px;
    padding: 2px;
}

/* The bottom half button on the right side (decrease value) */
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #1E2330;
    border: none;
    border-bottom-right-radius: 5px;
    width: 28px;
    padding: 2px;
}

/* Up/down buttons turn red when hovered */
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #FF4A3D;
}

/* The up arrow icon inside the up-button */
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url(%%ASSETS%%/arrow-up.png);
    width: 10px;
    height: 7px;
}

/* The down arrow icon inside the down-button */
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url(%%ASSETS%%/arrow-down.png);
    width: 10px;
    height: 7px;
}

/* ===== PUSH BUTTON ===== */

/* Primary buttons like "CALCULATE STRATEGY" and "CALCULATE PRESSURES" */
QPushButton {
    background-color: #FF4A3D;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
    min-height: 20px;
}

/* Primary button when hovered — lighter red */
QPushButton:hover {
    background-color: #FF6255;
}

/* Primary button when clicked — darker red */
QPushButton:pressed {
    background-color: #D93D32;
}

/* Primary button when disabled — grayed out */
QPushButton:disabled {
    background-color: #2A3040;
    color: #5A6275;
}

/* Secondary buttons (dark background, used for less important actions) */
QPushButton[class="secondary"] {
    background-color: #1E2330;
    color: #B0B8C8;
    border: 1px solid #2A3040;
}

/* Secondary button when hovered */
QPushButton[class="secondary"]:hover {
    background-color: #2A3040;
    color: #E0E4EC;
}

/* ===== SCROLL BAR ===== */

/* The vertical scrollbar track */
QScrollBar:vertical {
    background: #0D0F14;
    width: 8px;
    margin: 0;
}

/* The draggable handle inside the scrollbar */
QScrollBar::handle:vertical {
    background: #2A3040;
    border-radius: 4px;
    min-height: 30px;
}

/* Scrollbar handle turns red when hovered */
QScrollBar::handle:vertical:hover {
    background: #FF4A3D;
}

/* Hide the top/bottom arrow buttons on the scrollbar */
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* The vertical separator line between left inputs and right results */
QFrame[frameShape="5"] {
    color: #1E2330;
    max-width: 1px;
}

/* ===== TOOL TIP ===== */

/* Popup hint that appears when you hover over a widget */
QToolTip {
    background-color: #1E2330;
    color: #E0E4EC;
    border: 1px solid #2A3040;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
}
"""

DARK_RACING_THEME = _DARK_RACING_THEME.replace("%%ASSETS%%", _ASSETS)
