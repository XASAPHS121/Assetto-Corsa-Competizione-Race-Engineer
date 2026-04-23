"""
ACC Race Engineer — Fuel Calculator Tab
PyQt6 widget for fuel strategy calculations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.car_data import CarDatabase
from core.fuel_calculator import calculate_fuel_strategy, calculate_laps_from_duration


class ResultCard(QWidget):
    """A styled card to display a single result value."""

    def __init__(self, label_text: str, unit_text: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(2)

        self.label = QLabel(label_text)
        self.label.setProperty("class", "result-label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.value_label = QLabel("—")
        self.value_label.setProperty("class", "value-large")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.unit_label = QLabel(unit_text)
        self.unit_label.setProperty("class", "unit")
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)

        self.setStyleSheet("""
            ResultCard {
                background-color: #161A24;
                border: 1px solid #1E2330;
                border-radius: 8px;
            }
        """)

    def set_value(self, value: str, accent: bool = False):
        self.value_label.setText(value)
        if accent:
            self.value_label.setProperty("class", "value-accent")
        else:
            self.value_label.setProperty("class", "value-large")
        self.value_label.style().unpolish(self.value_label)
        self.value_label.style().polish(self.value_label)


class FuelCalculatorTab(QWidget):
    """Fuel Calculator tab for the ACC Race Engineer."""

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
        input_panel.setMaximumWidth(440)
        input_panel.setMinimumWidth(400)
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

        tank_row = QHBoxLayout()
        car_grid.addWidget(QLabel("Tank Capacity"), 2, 0)
        self.tank_label = QLabel("— L")
        self.tank_label.setStyleSheet("color: #FF4A3D; font-weight: 700; font-size: 14px;")
        car_grid.addWidget(self.tank_label, 2, 1)

        input_layout.addWidget(car_group)

        # Race Parameters Group
        race_group = QGroupBox("RACE PARAMETERS")
        race_grid = QGridLayout(race_group)
        race_grid.setSpacing(10)

        race_grid.addWidget(QLabel("Race Mode"), 0, 0)
        self.race_mode_combo = QComboBox()
        self.race_mode_combo.addItems(["Fixed Laps", "Timed Race"])
        race_grid.addWidget(self.race_mode_combo, 0, 1)

        self.race_laps_label = QLabel("Number of Laps")
        race_grid.addWidget(self.race_laps_label, 1, 0)
        self.race_laps_spin = QSpinBox()
        self.race_laps_spin.setRange(1, 999)
        self.race_laps_spin.setValue(30)
        race_grid.addWidget(self.race_laps_spin, 1, 1)

        self.duration_label = QLabel("Race Duration (min)")
        self.duration_label.setVisible(False)
        race_grid.addWidget(self.duration_label, 2, 0)
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 1440)
        self.duration_spin.setValue(60)
        self.duration_spin.setVisible(False)
        race_grid.addWidget(self.duration_spin, 2, 1)

        self.laptime_label = QLabel("Avg Lap Time")
        self.laptime_label.setVisible(False)
        race_grid.addWidget(self.laptime_label, 3, 0)

        laptime_row = QWidget()
        laptime_h = QHBoxLayout(laptime_row)
        laptime_h.setContentsMargins(0, 0, 0, 0)
        laptime_h.setSpacing(6)

        self.laptime_min_spin = QSpinBox()
        self.laptime_min_spin.setRange(0, 9)
        self.laptime_min_spin.setValue(2)
        self.laptime_min_spin.setSuffix(" min")

        self.laptime_sec_spin = QDoubleSpinBox()
        self.laptime_sec_spin.setRange(0.0, 59.9)
        self.laptime_sec_spin.setValue(0.0)
        self.laptime_sec_spin.setDecimals(1)
        self.laptime_sec_spin.setSuffix(" sec")
        self.laptime_sec_spin.setSingleStep(0.1)

        laptime_h.addWidget(self.laptime_min_spin)
        laptime_h.addWidget(self.laptime_sec_spin)

        laptime_row.setVisible(False)
        self.laptime_row = laptime_row
        race_grid.addWidget(laptime_row, 3, 1)

        input_layout.addWidget(race_group)

        # Fuel Parameters Group
        fuel_group = QGroupBox("FUEL DATA")
        fuel_grid = QGridLayout(fuel_group)
        fuel_grid.setSpacing(10)

        fuel_grid.addWidget(QLabel("Avg Fuel / Lap"), 0, 0)
        self.fuel_per_lap_spin = QDoubleSpinBox()
        self.fuel_per_lap_spin.setRange(0.1, 20.0)
        self.fuel_per_lap_spin.setValue(3.0)
        self.fuel_per_lap_spin.setDecimals(2)
        self.fuel_per_lap_spin.setSuffix(" L")
        self.fuel_per_lap_spin.setSingleStep(0.1)
        fuel_grid.addWidget(self.fuel_per_lap_spin, 0, 1)

        engine_map_hint = QLabel("Value depends on your engine map. Use Map 1 for aggressive pace, Map 2-3 to save fuel.")
        engine_map_hint.setStyleSheet("color: #5A6275; font-size: 10px; font-style: italic;")
        engine_map_hint.setWordWrap(True)
        fuel_grid.addWidget(engine_map_hint, 1, 0, 1, 2)

        fuel_grid.addWidget(QLabel("Formation Laps"), 2, 0)
        self.formation_laps_spin = QSpinBox()
        self.formation_laps_spin.setRange(0, 5)
        self.formation_laps_spin.setValue(1)
        fuel_grid.addWidget(self.formation_laps_spin, 2, 1)

        fuel_grid.addWidget(QLabel("Safety Margin"), 3, 0)
        self.safety_margin_spin = QDoubleSpinBox()
        self.safety_margin_spin.setRange(0.0, 5.0)
        self.safety_margin_spin.setValue(1.0)
        self.safety_margin_spin.setDecimals(1)
        self.safety_margin_spin.setSuffix(" laps")
        self.safety_margin_spin.setSingleStep(0.5)
        fuel_grid.addWidget(self.safety_margin_spin, 3, 1)

        input_layout.addWidget(fuel_group)

        # Calculate Button
        self.calc_button = QPushButton("CALCULATE STRATEGY")
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

        results_heading = QLabel("FUEL STRATEGY RESULTS")
        results_heading.setProperty("class", "heading")
        results_heading.setAlignment(Qt.AlignmentFlag.AlignLeft)
        results_layout.addWidget(results_heading)

        # Top row of result cards
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        self.card_total_fuel = ResultCard("TOTAL FUEL NEEDED", "LITERS")
        self.card_laps_per_tank = ResultCard("LAPS PER FULL TANK", "LAPS")
        self.card_pit_stops = ResultCard("PIT STOPS REQUIRED", "STOPS")
        top_row.addWidget(self.card_total_fuel)
        top_row.addWidget(self.card_laps_per_tank)
        top_row.addWidget(self.card_pit_stops)
        results_layout.addLayout(top_row)

        # Bottom row of result cards
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)
        self.card_fuel_per_stop = ResultCard("FUEL PER STOP", "LITERS")
        self.card_formation_fuel = ResultCard("FORMATION LAP FUEL", "LITERS")
        self.card_fuel_finish = ResultCard("FUEL AT FINISH", "LITERS")
        bottom_row.addWidget(self.card_fuel_per_stop)
        bottom_row.addWidget(self.card_formation_fuel)
        bottom_row.addWidget(self.card_fuel_finish)
        results_layout.addLayout(bottom_row)

        # Stint Breakdown
        self.stint_group = QGroupBox("STINT BREAKDOWN")
        self.stint_layout = QVBoxLayout(self.stint_group)
        self.stint_layout.setSpacing(6)
        self.stint_info_label = QLabel("Calculate a strategy to see stint breakdown.")
        self.stint_info_label.setStyleSheet("color: #5A6275; font-style: italic;")
        self.stint_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stint_layout.addWidget(self.stint_info_label)
        results_layout.addWidget(self.stint_group)

        # Advisor Notes
        self.notes_group = QGroupBox("STRATEGY NOTES")
        self.notes_layout = QVBoxLayout(self.notes_group)
        self.notes_layout.setSpacing(4)
        notes_placeholder = QLabel("Calculate a strategy to see advisor notes.")
        notes_placeholder.setStyleSheet("color: #5A6275; font-style: italic;")
        notes_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notes_layout.addWidget(notes_placeholder)
        results_layout.addWidget(self.notes_group)

        results_layout.addStretch()
        main_layout.addWidget(results_panel, stretch=1)

    def _connect_signals(self):
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        self.car_combo.currentTextChanged.connect(self._on_car_changed)
        self.race_mode_combo.currentTextChanged.connect(self._on_race_mode_changed)
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
        car_name = self.car_combo.currentText()
        if not car_name:
            return
        tank = self.car_db.get_fuel_tank(car_name)
        self.tank_label.setText(f"{tank:.0f} L")

    def _on_race_mode_changed(self, mode: str):
        is_timed = mode == "Timed Race"
        self.race_laps_label.setVisible(not is_timed)
        self.race_laps_spin.setVisible(not is_timed)
        self.duration_label.setVisible(is_timed)
        self.duration_spin.setVisible(is_timed)
        self.laptime_label.setVisible(is_timed)
        self.laptime_row.setVisible(is_timed)

    def _calculate(self):
        car_name = self.car_combo.currentText()
        if not car_name:
            return

        tank = self.car_db.get_fuel_tank(car_name)
        fuel_per_lap = self.fuel_per_lap_spin.value()

        if self.race_mode_combo.currentText() == "Timed Race":
            lap_time_sec = self.laptime_min_spin.value() * 60 + self.laptime_sec_spin.value()
            race_laps = calculate_laps_from_duration(
                self.duration_spin.value(),
                lap_time_sec,
            )
        else:
            race_laps = self.race_laps_spin.value()

        strategy = calculate_fuel_strategy(
            fuel_per_lap=fuel_per_lap,
            tank_capacity=tank,
            race_laps=race_laps,
            formation_laps=self.formation_laps_spin.value(),
            safety_margin_laps=self.safety_margin_spin.value(),
        )

        # Update result cards
        self.card_total_fuel.set_value(f"{strategy.total_fuel_needed:.1f}", accent=True)
        self.card_laps_per_tank.set_value(f"{strategy.laps_per_full_tank}")
        self.card_pit_stops.set_value(f"{strategy.pit_stops_needed}", accent=True)
        self.card_fuel_per_stop.set_value(f"{strategy.fuel_per_stop:.1f}")
        self.card_formation_fuel.set_value(f"{strategy.formation_lap_fuel:.1f}")
        self.card_fuel_finish.set_value(f"{strategy.fuel_at_finish:.1f}")

        # Update stint breakdown
        self._update_stint_breakdown(strategy)

        # Update advisor notes
        self._update_notes(strategy)

    def _update_stint_breakdown(self, strategy):
        # Clear old stint info
        while self.stint_layout.count():
            item = self.stint_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layouts
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        # Table container
        table = QFrame()
        table.setStyleSheet("""
            QFrame {
                background-color: #12151C;
                border: none;
                border-radius: 0px;
            }
        """)
        table_layout = QGridLayout(table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Column headers
        headers = ["STINT", "LAPS", "FUEL LOAD", "FUEL USED", "PIT STOPS"]
        header_style = "color: #0076C5; font-size: 14px; font-weight: 700; letter-spacing: 1px; padding: 8px 6px; background-color: #161A24;"
        aligns = [
            Qt.AlignmentFlag.AlignCenter,
            Qt.AlignmentFlag.AlignCenter,
            Qt.AlignmentFlag.AlignCenter,
            Qt.AlignmentFlag.AlignCenter,
            Qt.AlignmentFlag.AlignCenter,
        ]

        for col, header_text in enumerate(headers):
            lbl = QLabel(header_text)
            lbl.setStyleSheet(header_style)
            lbl.setAlignment(aligns[col] | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(lbl, 0, col)

        # Separator under header
        sep = QFrame()
        sep.setFixedHeight(20)
        sep.setStyleSheet("background-color: #12151C;")
        table_layout.addWidget(sep, 1, 0, 1, 5)

        # Data rows
        total_stints = len(strategy.stint_plan)
        for i, (stint_laps, fuel_load) in enumerate(
            zip(strategy.stint_plan, strategy.fuel_load_per_stint)
        ):
            row = i + 2  # offset for header + separator
            stint_num = i + 1
            is_last = (i == total_stints - 1)

            # Fuel consumed this stint
            fuel_consumed = stint_laps * strategy.fuel_per_lap
            if i == 0:
                fuel_consumed += strategy.formation_lap_fuel

            # Alternating row background
            bg = "#161A24" if i % 2 == 0 else "#12151C"

            # Stint number
            stint_lbl = QLabel(f"  STINT {stint_num}")
            stint_lbl.setStyleSheet(f"color: #FF4A3D; font-weight: 700; font-size: 14px; letter-spacing: 1px; padding: 10px 16px; background-color: {bg};")
            stint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(stint_lbl, row, 0)

            # Laps
            laps_lbl = QLabel(f"{stint_laps}")
            laps_lbl.setStyleSheet(f"color: #E0E4EC; font-weight: 700; font-size: 14px; padding: 10px 16px; background-color: {bg};")
            laps_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(laps_lbl, row, 1)

            # Fuel load
            load_lbl = QLabel(f"{fuel_load:.1f} L")
            load_lbl.setStyleSheet(f"color: #E0E4EC; font-weight: 700; font-size: 14px; padding: 10px 16px; background-color: {bg};")
            load_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(load_lbl, row, 2)

            # Fuel used
            used_lbl = QLabel(f"{fuel_consumed:.1f} L")
            used_lbl.setStyleSheet(f"color: #E0E4EC; font-weight: 700; font-size: 14px; padding: 10px 16px; background-color: {bg};")
            used_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(used_lbl, row, 3)

            # Pit / Finish badge
            if is_last:
                badge_text = "FINISH"
                badge_color = "#22C55E"
            else:
                badge_text = "PIT"
                badge_color = "#FF4A3D"

            badge = QLabel(f"  {badge_text}  ")
            badge.setStyleSheet(
                f"color: {badge_color}; font-size: 14px; font-weight: 700; letter-spacing: 1px; "
                f"border: 1px solid {badge_color}; border-radius: 0px; padding: 10px 16px; "
                f"background-color: {bg};"
            )
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table_layout.addWidget(badge, row, 4)

        self.stint_layout.addWidget(table)
        self.stint_layout.addStretch()

    def _update_notes(self, strategy):
        """Generate and display strategy advisor notes based on calculated fuel strategy."""
        # Clear old notes
        while self.notes_layout.count():
            item = self.notes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        notes = []
        fuel_per_lap = strategy.fuel_per_lap
        tank = strategy.tank_capacity
        total_fuel = strategy.total_fuel_needed
        pit_stops = strategy.pit_stops_needed

        # Engine map reminder
        notes.append(("info", "Fuel per lap varies by engine map. Map 1 = aggressive/high use, Map 2-3 = conservative/lower use. Match your input to your race map."))

        # Fuel load tradeoff
        load_pct = (total_fuel / tank) * 100
        if load_pct >= 90:
            notes.append(("warn", f"You are loading {load_pct:.0f}% of tank capacity. Heavy fuel load will hurt lap times and increase tire wear early in each stint."))
        elif load_pct <= 50:
            notes.append(("good", f"Light fuel load ({load_pct:.0f}% of tank). Expect better lap times and lower tire wear — but consider fuel saving if the race is long."))
        else:
            notes.append(("info", f"Moderate fuel load ({load_pct:.0f}% of tank). Good balance between pace and race completion margin."))

        # Pit stop strategy tip
        if pit_stops == 0:
            notes.append(("good", "No pit stop required. You can complete the race on one tank — but watch consumption if you push hard."))
        elif pit_stops == 1:
            notes.append(("info", "One pit stop strategy. Plan your stop around traffic and safety car windows for best time gain."))
        else:
            notes.append(("warn", f"{pit_stops} pit stops required. Each stop costs ~25-30 seconds. Consider if fuel saving could reduce stops."))

        # Safety fuel note
        notes.append(("info", f"Safety margin: {strategy.safety_fuel:.1f} L ({strategy.safety_fuel / fuel_per_lap:.1f} laps). Adjust if you plan aggressive fuel saving."))

        # Render notes
        for note_type, text in notes:
            row = QFrame()
            row.setStyleSheet("""
                QFrame {
                    background-color: #161A24;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                }
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 6, 10, 6)
            row_layout.setSpacing(10)

            dot_colors = {"info": "#8891A5", "warn": "#FF4A3D", "good": "#22C55E"}
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {dot_colors[note_type]}; font-size: 10px; background: transparent;")
            dot.setFixedWidth(12)

            label = QLabel(text)
            label.setStyleSheet("color: #B0B8C8; font-size: 12px; background: transparent;")
            label.setWordWrap(True)

            row_layout.addWidget(dot)
            row_layout.addWidget(label, stretch=1)
            self.notes_layout.addWidget(row)

        self.notes_layout.addStretch()
