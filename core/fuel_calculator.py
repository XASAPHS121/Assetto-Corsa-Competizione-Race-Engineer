"""
ACC Race Engineer — Fuel Calculator Module
Calculates fuel strategy for races based on car data and user inputs.
"""

from dataclasses import dataclass, field
import math


@dataclass
class FuelStrategy:
    """Result of a fuel calculation."""
    fuel_per_lap: float
    tank_capacity: float
    race_laps: int
    total_fuel_needed: float
    laps_per_full_tank: int
    pit_stops_needed: int
    fuel_per_stop: float
    fuel_at_finish: float
    formation_lap_fuel: float
    safety_fuel: float
    stint_plan: list[int] = field(default_factory=list)
    fuel_load_per_stint: list[float] = field(default_factory=list)


def calculate_fuel_strategy(
    fuel_per_lap: float,
    tank_capacity: float,
    race_laps: int,
    formation_laps: int = 1,
    formation_lap_multiplier: float = 0.5,
    safety_margin_laps: float = 1.0,
) -> FuelStrategy:
    """
    Calculate optimal fuel strategy for a race.

    Args:
        fuel_per_lap: Average fuel consumption per lap in liters.
        tank_capacity: Maximum fuel tank capacity in liters.
        race_laps: Total number of racing laps.
        formation_laps: Number of formation/warm-up laps.
        formation_lap_multiplier: Fuel multiplier for formation laps (lower speed).
        safety_margin_laps: Extra laps of fuel to carry as safety margin.

    Returns:
        FuelStrategy with all computed values.
    """
    if fuel_per_lap <= 0:
        raise ValueError("Fuel per lap must be positive.")
    if tank_capacity <= 0:
        raise ValueError("Tank capacity must be positive.")
    if race_laps <= 0:
        raise ValueError("Race laps must be positive.")

    formation_fuel = formation_laps * fuel_per_lap * formation_lap_multiplier
    safety_fuel = safety_margin_laps * fuel_per_lap

    total_race_fuel = (race_laps * fuel_per_lap) + formation_fuel + safety_fuel

    # Max racing laps on a full tank (informational only, not used for stint planning)
    laps_per_full_tank = int(tank_capacity / fuel_per_lap)

    # Build the stint plan
    stint_plan, fuel_loads = _build_stint_plan(
        fuel_per_lap=fuel_per_lap,
        tank_capacity=tank_capacity,
        race_laps=race_laps,
        formation_fuel=formation_fuel,
        safety_fuel=safety_fuel,
    )

    pit_stops = len(stint_plan) - 1

    # Fuel per stop: average refuel amount (0 if no stops)
    if pit_stops > 0:
        fuel_per_stop = round(sum(fuel_loads[1:]) / pit_stops, 2)
    else:
        fuel_per_stop = 0.0

    # Fuel at finish: total fuel loaded minus total consumed
    total_fuel_loaded = sum(fuel_loads)
    fuel_at_finish = total_fuel_loaded - total_race_fuel

    return FuelStrategy(
        fuel_per_lap=fuel_per_lap,
        tank_capacity=tank_capacity,
        race_laps=race_laps,
        total_fuel_needed=round(total_race_fuel, 2),
        laps_per_full_tank=laps_per_full_tank,
        pit_stops_needed=pit_stops,
        fuel_per_stop=fuel_per_stop,
        fuel_at_finish=round(max(fuel_at_finish, 0), 2),
        formation_lap_fuel=round(formation_fuel, 2),
        safety_fuel=round(safety_fuel, 2),
        stint_plan=stint_plan,
        fuel_load_per_stint=fuel_loads,
    )


def _build_stint_plan(
    fuel_per_lap: float,
    tank_capacity: float,
    race_laps: int,
    formation_fuel: float,
    safety_fuel: float,
) -> tuple[list[int], list[float]]:
    """
    Build a realistic stint plan respecting tank capacity.

    Returns:
        (stint_plan, fuel_loads) — list of lap counts and fuel to load per stint.
    """
    total_race_fuel = (race_laps * fuel_per_lap) + formation_fuel + safety_fuel

    if total_race_fuel <= tank_capacity:
        # No pit stop needed — single stint
        fuel_load = min(math.ceil(total_race_fuel), tank_capacity)
        return [race_laps], [round(float(fuel_load), 2)]

    # First stint: formation fuel reduces available capacity for racing laps
    first_stint_available = tank_capacity - formation_fuel
    first_stint_laps = int(first_stint_available / fuel_per_lap)
    first_stint_laps = max(first_stint_laps, 1)

    # Subsequent stints: full tank available for racing laps
    max_laps_per_stint = int(tank_capacity / fuel_per_lap)

    # Build stint list
    stint_plan = []
    laps_remaining = race_laps

    # First stint
    stint_laps = min(first_stint_laps, laps_remaining)
    stint_plan.append(stint_laps)
    laps_remaining -= stint_laps

    # Middle and final stints
    while laps_remaining > 0:
        stint_laps = min(max_laps_per_stint, laps_remaining)
        stint_plan.append(stint_laps)
        laps_remaining -= stint_laps

    # Calculate fuel loads per stint
    fuel_loads = []
    for i, laps in enumerate(stint_plan):
        fuel_needed = laps * fuel_per_lap
        if i == 0:
            fuel_needed += formation_fuel
        # Add safety fuel proportionally to the last stint, or spread it
        if i == len(stint_plan) - 1:
            fuel_needed += safety_fuel
        fuel_load = min(math.ceil(fuel_needed), tank_capacity)
        fuel_loads.append(round(float(fuel_load), 2))

    return stint_plan, fuel_loads


def calculate_laps_from_duration(
    race_duration_minutes: float,
    avg_lap_time_seconds: float,
) -> int:
    """Convert a timed race into estimated lap count."""
    if race_duration_minutes <= 0:
        raise ValueError("Race duration must be positive.")
    if avg_lap_time_seconds <= 0:
        raise ValueError("Lap time must be positive.")
    total_seconds = race_duration_minutes * 60
    return math.ceil(total_seconds / avg_lap_time_seconds)
