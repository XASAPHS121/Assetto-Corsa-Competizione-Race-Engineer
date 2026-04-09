"""
ACC Race Engineer — Main Window
The root application window with tab navigation.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from core.car_data import CarDatabase
from ui.fuel_tab import FuelCalculatorTab
from ui.tire_tab import TireAdvisorTab


class MainWindow(QMainWindow):
    """ACC Race Engineer main application window."""

    def __init__(self, car_db: CarDatabase):
        super().__init__()
        self.car_db = car_db
        self.setWindowTitle("Assetto Corsa Competizione  Race  Engineer")
        from core.paths import get_assets_path
        import os
        icon_path = os.path.join(get_assets_path(), "ACC_ICON.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(1500, 1100)
        self.resize(1500, 780)

        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ===== Header Bar =====
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: #0A0C10;
                border-bottom: 1px solid #1E2330;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # App title — centered
        title = QLabel("BOX BOX")
        title.setStyleSheet("color: #FF4A3D; font-family: 'Segoe UI'; font-size: 20px; font-weight: 700; letter-spacing: 4px; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title, stretch=1)

        root_layout.addWidget(header)

        # ===== Tab Widget =====
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.fuel_tab = FuelCalculatorTab(self.car_db)
        self.tire_tab = TireAdvisorTab(self.car_db)

        self.tabs.addTab(self.fuel_tab, "⛽  FUEL CALCULATOR")
        self.tabs.addTab(self.tire_tab, "🔧  TIRE ADVISOR")

        root_layout.addWidget(self.tabs)

        # ===== Status Bar =====
        status = QWidget()
        status.setFixedHeight(28)
        status.setStyleSheet("""
            QWidget {
                background-color: #0A0C10;
                border-top: 1px solid #1E2330;
            }
        """)
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(16, 0, 16, 0)

        cars_loaded = QLabel(f"{len(self.car_db.get_all_car_names())} cars loaded")
        cars_loaded.setStyleSheet("color: #3A3F50; font-size: 10px; background: transparent;")
        status_layout.addWidget(cars_loaded)

        status_layout.addStretch()

        credit = QLabel("Built for Assetto Corsa Competizione")
        credit.setStyleSheet("color: #3A3F50; font-size: 10px; background: transparent;")
        status_layout.addWidget(credit)

        root_layout.addWidget(status)
