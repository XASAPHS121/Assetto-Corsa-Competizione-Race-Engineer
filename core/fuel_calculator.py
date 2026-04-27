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
    stint_limited_by: list[str] = field(default_factory=list)
    max_stint_minutes: float = 0.0
    avg_lap_time_seconds: float = 0.0


def calculate_fuel_strategy(
    fuel_per_lap: float,
    tank_capacity: float,
    race_laps: int,
    formation_laps: int = 1,
    formation_lap_multiplier: float = 0.5,
    safety_margin_laps: float = 1.0,
    max_stint_minutes: float = 0.0,
    avg_lap_time_seconds: float = 0.0,
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
        max_stint_minutes: Optional max stint duration (0 = disabled).
        avg_lap_time_seconds: Avg lap time, required when max_stint_minutes > 0.

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
    stint_plan, fuel_loads, limited_by = _build_stint_plan(
        fuel_per_lap=fuel_per_lap,
        tank_capacity=tank_capacity,
        race_laps=race_laps,
        formation_fuel=formation_fuel,
        safety_fuel=safety_fuel,
        max_stint_minutes=max_stint_minutes,
        avg_lap_time_seconds=avg_lap_time_seconds,
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
        stint_limited_by=limited_by,
        max_stint_minutes=max_stint_minutes,
        avg_lap_time_seconds=avg_lap_time_seconds,
    )


def _build_stint_plan(
    fuel_per_lap: float,
    tank_capacity: float,
    race_laps: int,
    formation_fuel: float,
    safety_fuel: float,
    max_stint_minutes: float = 0.0,
    avg_lap_time_seconds: float = 0.0,
) -> tuple[list[int], list[float], list[str]]:
    """
    Build a realistic stint plan respecting tank capacity and optional time limit.

    Returns:
        (stint_plan, fuel_loads, limited_by) — laps, fuel, and what limited each stint.
    """
    # Compute time-based stint limit if enabled
    time_limit_active = max_stint_minutes > 0 and avg_lap_time_seconds > 0
    if time_limit_active:
        max_laps_by_time = int((max_stint_minutes * 60) / avg_lap_time_seconds)
        max_laps_by_time = max(max_laps_by_time, 1)
    else:
        max_laps_by_time = race_laps  # effectively no time limit

    total_race_fuel = (race_laps * fuel_per_lap) + formation_fuel + safety_fuel

    # Single-stint check: only if fuel AND time both allow it
    if total_race_fuel <= tank_capacity and race_laps <= max_laps_by_time:
        fuel_load = min(math.ceil(total_race_fuel), tank_capacity)
        return [race_laps], [round(float(fuel_load), 2)], ["finish"]

    # First stint capacity (formation fuel reduces available fuel)
    first_stint_available = tank_capacity - formation_fuel
    first_stint_fuel_laps = max(int(first_stint_available / fuel_per_lap), 1)

    # Other stints capacity
    other_stint_fuel_laps = max(int(tank_capacity / fuel_per_lap), 1)

    stint_plan: list[int] = []
    limited_by: list[str] = []
    laps_remaining = race_laps

    while laps_remaining > 0:
        is_first = len(stint_plan) == 0
        fuel_cap = first_stint_fuel_laps if is_first else other_stint_fuel_laps
        time_cap = max_laps_by_time

        # Whichever is smaller wins
        cap = min(fuel_cap, time_cap, laps_remaining)
        stint_plan.append(cap)
        laps_remaining -= cap

        # Determine what limited this stint
        if cap == laps_remaining + cap and laps_remaining == 0:
            # This was the final stint (race ended naturally)
            limited_by.append("finish")
        elif time_limit_active and time_cap < fuel_cap:
            limited_by.append("time")
        else:
            limited_by.append("fuel")

    # Last stint always reads "finish" since the race ended there
    if limited_by:
        limited_by[-1] = "finish"

    # Calculate fuel loads per stint
    fuel_loads = []
    for i, laps in enumerate(stint_plan):
        fuel_needed = laps * fuel_per_lap
        if i == 0:
            fuel_needed += formation_fuel
        if i == len(stint_plan) - 1:
            fuel_needed += safety_fuel
        fuel_load = min(math.ceil(fuel_needed), tank_capacity)
        fuel_loads.append(round(float(fuel_load), 2))

    return stint_plan, fuel_loads, limited_by


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
