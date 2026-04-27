"""
ACC Race Engineer — Session Exporter
Saves fuel and tire calculation results as JSON and TXT files
so users can reference them without reopening the app.
"""

import json
import os
import re
from datetime import datetime

from core.paths import get_exports_dir


def _safe_filename(text: str) -> str:
    """Strip characters that aren't safe for Windows filenames."""
    return re.sub(r'[<>:"/\\|?*]', "_", text).strip()


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M")


def export_fuel_strategy(car_name: str, strategy, race_mode: str) -> tuple[str, str]:
    """Save a fuel strategy as JSON and TXT. Returns (json_path, txt_path)."""
    exports = get_exports_dir("Fuel Calculator")
    safe_car = _safe_filename(car_name)
    base_name = f"Fuel_{safe_car}_{_timestamp()}"

    # JSON payload
    payload = {
        "type": "fuel_strategy",
        "car": car_name,
        "date": datetime.now().isoformat(timespec="seconds"),
        "race_mode": race_mode,
        "race_laps": strategy.race_laps,
        "fuel_per_lap": strategy.fuel_per_lap,
        "tank_capacity": strategy.tank_capacity,
        "total_fuel_needed": strategy.total_fuel_needed,
        "laps_per_full_tank": strategy.laps_per_full_tank,
        "pit_stops_needed": strategy.pit_stops_needed,
        "fuel_per_stop": strategy.fuel_per_stop,
        "fuel_at_finish": strategy.fuel_at_finish,
        "formation_lap_fuel": strategy.formation_lap_fuel,
        "safety_fuel": strategy.safety_fuel,
        "stint_plan": strategy.stint_plan,
        "fuel_load_per_stint": strategy.fuel_load_per_stint,
        "stint_limited_by": strategy.stint_limited_by,
        "max_stint_minutes": strategy.max_stint_minutes,
        "avg_lap_time_seconds": strategy.avg_lap_time_seconds,
    }

    json_path = os.path.join(exports, base_name + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # Human-readable TXT
    lines = [
        "=" * 50,
        "ACC RACE ENGINEER - FUEL STRATEGY",
        "=" * 50,
        f"Car:               {car_name}",
        f"Date:              {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Race Mode:         {race_mode}",
        f"Race Laps:         {strategy.race_laps}",
        f"Fuel per Lap:      {strategy.fuel_per_lap:.2f} L",
        f"Tank Capacity:     {strategy.tank_capacity:.0f} L",
        "",
        "-" * 50,
        "RESULTS",
        "-" * 50,
        f"Total Fuel Needed: {strategy.total_fuel_needed:.1f} L",
        f"Laps per Tank:     {strategy.laps_per_full_tank}",
        f"Pit Stops:         {strategy.pit_stops_needed}",
        f"Fuel per Stop:     {strategy.fuel_per_stop:.1f} L",
        f"Formation Fuel:    {strategy.formation_lap_fuel:.1f} L",
        f"Safety Fuel:       {strategy.safety_fuel:.1f} L",
        f"Fuel at Finish:    {strategy.fuel_at_finish:.1f} L",
        "",
    ]

    if strategy.max_stint_minutes > 0:
        lines.append(f"Max Stint Duration: {strategy.max_stint_minutes:.0f} min (championship rule)")
        lines.append("")

    lines.append("-" * 50)
    lines.append("STINT BREAKDOWN")
    lines.append("-" * 50)
    for i, (laps, load) in enumerate(zip(strategy.stint_plan, strategy.fuel_load_per_stint)):
        limit = ""
        if strategy.stint_limited_by and i < len(strategy.stint_limited_by):
            limit_val = strategy.stint_limited_by[i]
            if limit_val == "time":
                limit = " [TIME]"
            elif limit_val == "fuel":
                limit = " [FUEL]"
        is_last = i == len(strategy.stint_plan) - 1
        end = "FINISH" if is_last else "PIT"
        lines.append(f"Stint {i+1}: {laps} laps | Load: {load:.1f} L | End: {end}{limit}")

    txt_path = os.path.join(exports, base_name + ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return json_path, txt_path


def export_tire_recommendation(
    car_name: str,
    condition_label: str,
    ambient_temp: float,
    track_temp: float,
    cold_pressures: dict,
    pressure_gain: float,
    optimal_hot_min: float,
    optimal_hot_max: float,
    notes: list[str] | None = None,
) -> tuple[str, str]:
    """Save tire pressure recommendation as JSON and TXT. Returns (json_path, txt_path)."""
    exports = get_exports_dir("Tire Advisor")
    safe_car = _safe_filename(car_name)
    base_name = f"Tires_{safe_car}_{_timestamp()}"

    payload = {
        "type": "tire_recommendation",
        "car": car_name,
        "date": datetime.now().isoformat(timespec="seconds"),
        "condition": condition_label,
        "ambient_temp_c": ambient_temp,
        "track_temp_c": track_temp,
        "cold_pressures_psi": cold_pressures,
        "estimated_pressure_gain_psi": pressure_gain,
        "optimal_hot_psi_min": optimal_hot_min,
        "optimal_hot_psi_max": optimal_hot_max,
        "notes": notes or [],
    }

    json_path = os.path.join(exports, base_name + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    lines = [
        "=" * 50,
        "ACC RACE ENGINEER - TIRE PRESSURES",
        "=" * 50,
        f"Car:           {car_name}",
        f"Date:          {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Condition:     {condition_label}",
        f"Ambient Temp:  {ambient_temp:.1f} C",
        f"Track Temp:    {track_temp:.1f} C",
        "",
        "-" * 50,
        "COLD PRESSURES (set in pits)",
        "-" * 50,
        f"  Front Left:  {cold_pressures.get('FL', 0):.1f} PSI",
        f"  Front Right: {cold_pressures.get('FR', 0):.1f} PSI",
        f"  Rear Left:   {cold_pressures.get('RL', 0):.1f} PSI",
        f"  Rear Right:  {cold_pressures.get('RR', 0):.1f} PSI",
        "",
        f"Estimated Pressure Gain: +{pressure_gain:.1f} PSI cold to hot",
        f"Target Hot Window:        {optimal_hot_min:.1f} - {optimal_hot_max:.1f} PSI",
    ]

    if notes:
        lines.extend(["", "-" * 50, "ADVISOR NOTES", "-" * 50])
        for note in notes:
            lines.append(f"- {note}")

    txt_path = os.path.join(exports, base_name + ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return json_path, txt_path
