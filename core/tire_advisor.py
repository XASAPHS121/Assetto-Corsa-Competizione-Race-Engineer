"""
ACC Race Engineer — Tire Advisor Module
Calculates recommended cold starting tire pressures based on car, weather, and temperature.

Key concept:
  - Cold pressures = what you set in the pits (lower, tires are cold)
  - Hot pressures = what tires reach on track (higher, tires heated up)
  - Optimal HOT pressure window: 26.6 — 27.0 PSI
  - The goal: recommend cold pressures that will reach the optimal hot window
"""

from dataclasses import dataclass


@dataclass
class TireRecommendation:
    """Result of a tire pressure calculation."""
    car_name: str
    weather_condition: str  # dry_hot, dry_mild, dry_cold, wet
    weather_label: str      # Human-readable: "Dry - Hot", etc.
    ambient_temp: float
    track_temp: float
    optimal_hot_min: float  # Optimal hot PSI min (26.6)
    optimal_hot_max: float  # Optimal hot PSI max (27.0)
    cold_pressures: dict[str, float]   # FL, FR, RL, RR — what to set in pits
    estimated_hot: dict[str, float]    # FL, FR, RL, RR — estimated on-track PSI
    temp_status: str        # "too_hot", "optimal", "too_cold"
    temp_delta: float       # How far track temp is from ideal range
    notes: list[str]


def classify_weather(ambient_temp: float, is_wet: bool) -> tuple[str, str]:
    """
    Classify weather condition based on ambient temperature and rain.

    Returns:
        (condition_key, human_label)
    """
    if is_wet:
        return "wet", "Wet"
    if ambient_temp > 30:
        return "dry_hot", "Dry - Hot"
    if ambient_temp >= 15:
        return "dry_mild", "Dry - Mild"
    return "dry_cold", "Dry - Cold"


def _estimate_pressure_gain(ambient_temp: float, track_temp: float) -> float:
    """
    Estimate how much PSI the tires will gain from cold to hot.
    Hotter conditions = more pressure gain.
    Typical gain is ~2.5 PSI in mild conditions, more in hot, less in cold.
    """
    avg_temp = (ambient_temp + track_temp) / 2.0
    # Base gain at 20C is ~2.5 PSI, scales with temperature
    base_gain = 2.5
    gain = base_gain + (avg_temp - 20.0) * 0.05
    return max(gain, 1.0)  # At minimum 1 PSI gain even in freezing conditions


def calculate_tire_recommendation(
    car_name: str,
    ambient_temp: float,
    track_temp: float,
    is_wet: bool,
    cold_pressures: dict[str, float],
    optimal_hot_psi: tuple[float, float],
) -> TireRecommendation:
    """
    Calculate recommended cold starting tire pressures for given conditions.

    Args:
        car_name: Name of the car.
        ambient_temp: Ambient air temperature in Celsius.
        track_temp: Track surface temperature in Celsius.
        is_wet: Whether the track is wet.
        cold_pressures: Base cold pressures for the classified condition {FL, FR, RL, RR}.
        optimal_hot_psi: (min, max) optimal hot tire pressure range.

    Returns:
        TireRecommendation with cold pressures to set and estimated hot pressures.
    """
    condition, label = classify_weather(ambient_temp, is_wet)
    hot_min, hot_max = optimal_hot_psi
    hot_target = (hot_min + hot_max) / 2.0  # 26.8 PSI target
    notes = []

    # Estimate pressure gain from cold to hot
    pressure_gain = _estimate_pressure_gain(ambient_temp, track_temp)

    # Estimate what the cold pressures will become when hot
    estimated_hot = {}
    for corner, cold_psi in cold_pressures.items():
        estimated_hot[corner] = round(cold_psi + pressure_gain, 1)

    # Check if estimated hot pressures are in the optimal window
    avg_estimated_hot = sum(estimated_hot.values()) / len(estimated_hot)

    if avg_estimated_hot > hot_max:
        temp_status = "too_hot"
        temp_delta = round(avg_estimated_hot - hot_max, 1)
    elif avg_estimated_hot < hot_min:
        temp_status = "too_cold"
        temp_delta = round(hot_min - avg_estimated_hot, 1)
    else:
        temp_status = "optimal"
        temp_delta = 0.0

    # Build advice notes
    notes.append(f"Estimated pressure gain (cold to hot): +{pressure_gain:.1f} PSI")

    if temp_status == "optimal":
        notes.append(f"Estimated hot pressures are within the optimal window ({hot_min}-{hot_max} PSI).")
        notes.append("These cold pressures should put you in the grip sweet spot.")
    elif temp_status == "too_hot":
        notes.append(f"Estimated hot pressures are {temp_delta:.1f} PSI above optimal.")
        notes.append("Consider lowering cold pressures or monitoring tire wear.")
    else:
        notes.append(f"Estimated hot pressures are {temp_delta:.1f} PSI below optimal.")
        notes.append("Tires may struggle to reach operating window — expect less grip early on.")

    if is_wet:
        notes.append("Wet conditions: cold pressures set higher to resist aquaplaning.")

    return TireRecommendation(
        car_name=car_name,
        weather_condition=condition,
        weather_label=label,
        ambient_temp=ambient_temp,
        track_temp=track_temp,
        optimal_hot_min=hot_min,
        optimal_hot_max=hot_max,
        cold_pressures=cold_pressures,
        estimated_hot=estimated_hot,
        temp_status=temp_status,
        temp_delta=temp_delta,
        notes=notes,
    )
