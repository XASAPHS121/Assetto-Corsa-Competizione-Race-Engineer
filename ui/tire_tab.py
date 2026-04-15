"""
ACC Race Engineer — Tire Advisor Tab
PyQt6 widget for tire pressure recommendations based on weather conditions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QComboBox, QDoubleSpinBox,
    QPushButton, QFrame, QSizePolicy, QToolButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.car_data import CarDatabase
from core.tire_advisor import (
    calculate_tire_recommendation, _estimate_pressure_gain,
)
from ui.fuel_tab import ResultCard


class TireAdvisorTab(QWidget):
    """Tire Advisor tab for the ACC Race Engineer."""

    def __init__(self, car_db: CarDatabase, parent=None):
        super().__init__(parent)
        self.car_db = car_db
        self._setup_ui()
        self._connect_signals()
        self._populate_classes()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ===== LEFT: Inputs =====
        input_panel = QWidget()
        input_panel.setMaximumWidth(380)
        input_panel.setMinimumWidth(340)
        input_layout = QVBoxLayout(input_panel)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)

        # Car Selection Group
        car_group = QGroupBox("CAR SELECTION")
        car_grid = QGridLayout(car_group)
        car_grid.setSpacing(10)

        car_grid.addWidget(QLabel("Class"), 0, 0)
        self.class_combo = QComboBox()
        car_grid.addWidget(self.class_combo, 0, 1)

        car_grid.addWidget(QLabel("Car"), 1, 0)
        self.car_combo = QComboBox()
        self.car_combo.setMaxVisibleItems(15)
        car_grid.addWidget(self.car_combo, 1, 1)

        input_layout.addWidget(car_group)

        # Weather Conditions Group
        weather_group = QGroupBox("WEATHER CONDITIONS")
        weather_grid = QGridLayout(weather_group)
        weather_grid.setSpacing(10)

        weather_grid.addWidget(QLabel("Track Condition"), 0, 0)
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(["Dry", "Wet"])
        weather_grid.addWidget(self.condition_combo, 0, 1)

        weather_grid.addWidget(QLabel("Ambient Temp"), 1, 0)
        self.ambient_temp_spin = QDoubleSpinBox()
        self.ambient_temp_spin.setRange(-10.0, 50.0)
        self.ambient_temp_spin.setValue(22.0)
        self.ambient_temp_spin.setDecimals(1)
        self.ambient_temp_spin.setSuffix(" °C")
        self.ambient_temp_spin.setSingleStep(0.5)
        weather_grid.addWidget(self.ambient_temp_spin, 1, 1)

        weather_grid.addWidget(QLabel("Track Temp"), 2, 0)
        self.track_temp_spin = QDoubleSpinBox()
        self.track_temp_spin.setRange(-5.0, 65.0)
        self.track_temp_spin.setValue(30.0)
        self.track_temp_spin.setDecimals(1)
        self.track_temp_spin.setSuffix(" °C")
        self.track_temp_spin.setSingleStep(0.5)
        weather_grid.addWidget(self.track_temp_spin, 2, 1)

        input_layout.addWidget(weather_group)

        # Current HOT PSI Group
        convert_group = QGroupBox("CURRENT HOT PSI  (optional)")
        convert_grid = QGridLayout(convert_group)
        convert_grid.setSpacing(10)

        hot_hint = QLabel("Enter PSI values shown in-game while tires are hot")
        hot_hint.setStyleSheet("color: #5A6275; font-size: 11px;")
        hot_hint.setWordWrap(True)
        convert_grid.addWidget(hot_hint, 0, 0, 1, 2)

        self._current_psi_spins = {}
        for i, corner in enumerate(["FL", "FR", "RL", "RR"]):
            row, col = divmod(i, 2)
            convert_grid.addWidget(QLabel(corner), row * 2 + 1, col)
            spin = QDoubleSpinBox()
            spin.setRange(20.0, 35.0)
            spin.setValue(27.0)
            spin.setDecimals(1)
            spin.setSuffix(" PSI")
            spin.setSingleStep(0.1)
            convert_grid.addWidget(spin, row * 2 + 2, col)
            self._current_psi_spins[corner] = spin

        input_layout.addWidget(convert_group)

        # Reference Group
        ref_group = QGroupBox("REFERENCE")
        ref_layout = QVBoxLayout(ref_group)
        optimal_label = QLabel("Optimal HOT Pressure: 26.6 — 27.0 PSI")
        optimal_label.setStyleSheet("color: #FF4A3D; font-weight: 700; font-size: 14px;")
        optimal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ref_layout.addWidget(optimal_label)
        hint_label = QLabel("Cold pressures in pits will rise as tires heat up on track")
        hint_label.setStyleSheet("color: #5A6275; font-size: 11px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setWordWrap(True)
        ref_layout.addWidget(hint_label)
        input_layout.addWidget(ref_group)

        # Calculate Button
        self.calc_button = QPushButton("CALCULATE PRESSURES")
        self.calc_button.setMinimumHeight(48)
        self.calc_button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        input_layout.addWidget(self.calc_button)

        input_layout.addStretch()
        main_layout.addWidget(input_panel)

        # ===== Vertical Separator =====
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        main_layout.addWidget(sep)

        # ===== RIGHT: Results =====
        results_panel = QWidget()
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(16)

        results_heading = QLabel("TIRE PRESSURE RECOMMENDATIONS")
        results_heading.setProperty("class", "heading")
        results_heading.setAlignment(Qt.AlignmentFlag.AlignLeft)
        results_layout.addWidget(results_heading)

        # Top row: condition cards
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        self.card_weather = ResultCard("WEATHER", "CONDITION")
        self.card_pressure_gain = ResultCard("PRESSURE GAIN", "COLD TO HOT")
        self.card_hot_status = ResultCard("HOT PRESSURE", "STATUS")
        top_row.addWidget(self.card_weather)
        top_row.addWidget(self.card_pressure_gain)
        top_row.addWidget(self.card_hot_status)
        results_layout.addLayout(top_row)

        # Cold pressures — what to set in pits
        cold_group = QGroupBox("SET IN PITS (COLD PSI)")
        cold_grid = QGridLayout(cold_group)
        cold_grid.setSpacing(16)

        self.cold_cards = {}
        self._base_pressures = {}
        self._adjustments = {}
        corners = [("FL", "FRONT LEFT", 0, 0), ("FR", "FRONT RIGHT", 0, 1),
                   ("RL", "REAR LEFT", 1, 0), ("RR", "REAR RIGHT", 1, 1)]

        for key, label, row, col in corners:
            card = self._create_pressure_corner(key, label)
            cold_grid.addWidget(card, row, col)
            self.cold_cards[key] = card
            self._base_pressures[key] = 0.0
            self._adjustments[key] = 0.0

        results_layout.addWidget(cold_group)

        # Notes section
        self.notes_group = QGroupBox("ADVISOR NOTES")
        self.notes_layout = QVBoxLayout(self.notes_group)
        self.notes_layout.setSpacing(6)
        self.notes_placeholder = QLabel("Select conditions and calculate to see recommendations.")
        self.notes_placeholder.setStyleSheet("color: #5A6275; font-style: italic;")
        self.notes_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notes_layout.addWidget(self.notes_placeholder)
        results_layout.addWidget(self.notes_group)

        results_layout.addStretch()
        main_layout.addWidget(results_panel, stretch=1)

    def _create_pressure_corner(self, corner_key: str, label_text: str) -> QFrame:
        """Create a styled frame for a tire corner with +/- adjustment buttons."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #161A24;
                border: 1px solid #1E2330;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        corner_label = QLabel(label_text)
        corner_label.setStyleSheet("color: #E0E4EC; font-size: 14px; font-weight: 700; letter-spacing: 1px;")
        corner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_row = QHBoxLayout()
        value_row.setSpacing(8)

        minus_btn = QPushButton("-")
        minus_btn.setFixedSize(40, 40)
        minus_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E2330;
                color: #B0B8C8;
                border: 1px solid #2A3040;
                border-radius: 6px;
                font-size: 28px;
                font-weight: 700;
                padding: 0;
            }
            QPushButton:hover { background-color: #FF4A3D; color: #FFFFFF; border-color: #FF4A3D; }
            QPushButton:pressed { background-color: #D93D32; }
        """)
        minus_btn.clicked.connect(lambda: self._adjust_pressure(corner_key, -0.1))

        value_label = QLabel("—")
        value_label.setObjectName("pressure_value")
        value_label.setStyleSheet("color: #FFFFFF; font-size: 28px; font-weight: 700;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(40, 40)
        plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E2330;
                color: #B0B8C8;
                border: 1px solid #2A3040;
                border-radius: 6px;
                font-size: 28px;
                font-weight: 700;
                padding: 0;
            }
            QPushButton:hover { background-color: #FF4A3D; color: #FFFFFF; border-color: #FF4A3D; }
            QPushButton:pressed { background-color: #D93D32; }
        """)
        plus_btn.clicked.connect(lambda: self._adjust_pressure(corner_key, +0.1))

        value_row.addWidget(minus_btn)
        value_row.addWidget(value_label, stretch=1)
        value_row.addWidget(plus_btn)

        delta_label = QLabel("")
        delta_label.setObjectName("pressure_delta")
        delta_label.setStyleSheet("color: #5A6275; font-size: 11px; font-weight: 600;")
        delta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(corner_label)
        layout.addLayout(value_row)
        layout.addWidget(delta_label)

        return frame

    def _connect_signals(self):
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        self.car_combo.currentTextChanged.connect(self._on_car_changed)
        self.calc_button.clicked.connect(self._calculate)

    def _populate_classes(self):
        self.class_combo.clear()
        for cls in self.car_db.classes:
            self.class_combo.addItem(cls.upper(), cls)
        if self.class_combo.count() > 0:
            self._on_class_changed()

    def _on_class_changed(self):
        class_key = self.class_combo.currentData()
        if not class_key:
            return
        self.car_combo.blockSignals(True)
        self.car_combo.clear()
        for car in self.car_db.get_cars_by_class(class_key):
            self.car_combo.addItem(car["name"])
        self.car_combo.blockSignals(False)
        if self.car_combo.count() > 0:
            self._on_car_changed()

    def _on_car_changed(self):
        for key in self._adjustments:
            self._adjustments[key] = 0.0

    def _adjust_pressure(self, corner: str, delta: float):
        """Adjust a corner's pressure by delta PSI."""
        if self._base_pressures[corner] == 0.0:
            return

        self._adjustments[corner] = round(self._adjustments[corner] + delta, 1)
        new_psi = round(self._base_pressures[corner] + self._adjustments[corner], 1)

        frame = self.cold_cards[corner]
        value_label = frame.findChild(QLabel, "pressure_value")
        delta_label = frame.findChild(QLabel, "pressure_delta")

        if value_label:
            value_label.setText(f"{new_psi:.1f}")

        if delta_label:
            adj = self._adjustments[corner]
            if adj == 0.0:
                delta_label.setText("")
            elif adj > 0:
                delta_label.setText(f"+{adj:.1f} from base")
                delta_label.setStyleSheet("color: #FF4A3D; font-size: 14px; font-weight: 600;")
            else:
                delta_label.setText(f"{adj:.1f} from base")
                delta_label.setStyleSheet("color: #4A9FFF; font-size: 14px; font-weight: 600;")

    def _calculate(self):
        car_name = self.car_combo.currentText()
        if not car_name:
            return

        ambient_temp = self.ambient_temp_spin.value()
        track_temp   = self.track_temp_spin.value()
        is_wet       = self.condition_combo.currentText() == "Wet"

        optimal_hot       = self.car_db.get_optimal_hot_psi(car_name)
        tire_split        = self.car_db.get_tire_split(car_name)
        wet_cold          = self.car_db.get_wet_cold_pressures(car_name)

        recommendation = calculate_tire_recommendation(
            car_name=car_name,
            ambient_temp=ambient_temp,
            track_temp=track_temp,
            is_wet=is_wet,
            tire_split_psi=tire_split,
            wet_cold_pressures=wet_cold,
            optimal_hot_psi=optimal_hot,
        )

        # Summary cards
        self.card_weather.set_value(recommendation.weather_label, accent=True)
        gain = _estimate_pressure_gain(track_temp)
        self.card_pressure_gain.set_value(f"+{gain:.2f}", accent=False)
        status_display = {"optimal": "IN WINDOW", "too_hot": "OVER", "too_cold": "UNDER"}
        self.card_hot_status.set_value(
            status_display[recommendation.temp_status],
            accent=recommendation.temp_status != "optimal",
        )

        # Update cold pressure cards
        # "CURRENT HOT PSI" inputs are what the user sees in-game while tires are hot.
        # We convert those to an estimated cold by subtracting the pressure gain,
        # then show how much the recommended cold differs from the user's current cold.
        for corner, frame in self.cold_cards.items():
            if corner in recommendation.cold_pressures:
                psi = recommendation.cold_pressures[corner]
                self._base_pressures[corner] = psi
                self._adjustments[corner] = 0.0

                value_label = frame.findChild(QLabel, "pressure_value")
                delta_label = frame.findChild(QLabel, "pressure_delta")
                if value_label:
                    value_label.setText(f"{psi:.1f}")
                    value_label.setStyleSheet("color: #22C55E; font-size: 28px; font-weight: 700;")
                if delta_label:
                    # User entered their current HOT psi; estimate their current cold
                    current_hot  = self._current_psi_spins[corner].value()
                    current_cold = round(current_hot - gain, 1)
                    diff = round(psi - current_cold, 1)
                    if diff == 0.0:
                        delta_label.setText("no change vs current")
                        delta_label.setStyleSheet("color: #5A6275; font-size: 14px; font-weight: 600;")
                    elif diff > 0:
                        delta_label.setText(f"+{diff:.1f} vs current cold")
                        delta_label.setStyleSheet("color: #FF4A3D; font-size: 14px; font-weight: 600;")
                    else:
                        delta_label.setText(f"{diff:.1f} vs current cold")
                        delta_label.setStyleSheet("color: #4A9FFF; font-size: 14px; font-weight: 600;")

        self._update_notes(recommendation.notes)

    def _update_notes(self, notes: list[str]):
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for note in notes:
            lbl = QLabel(f"  {note}")
            lbl.setStyleSheet("color: #B0B8C8; font-size: 13px; padding: 2px 0;")
            lbl.setWordWrap(True)
            self.notes_layout.addWidget(lbl)
        self.notes_layout.addStretch()
