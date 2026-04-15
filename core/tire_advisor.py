"""
ACC Race Engineer — Tire Advisor Module
Calculates recommended cold starting tire pressures based on car, weather, and temperature.

Key concept:
  - Cold pressures = what you set in the pits (tires are cold)
  - Hot pressures  = what tires reach on track (tires heated up)
  - Optimal HOT pressure window: 26.6 - 27.0 PSI
  - Rule: 0.1 PSI gain per every 2°C of track temperature above/below 25°C reference
  - Goal: recommend cold pressures that will reach the optimal hot window
"""

from dataclasses import dataclass, field


@dataclass
class TireRecommendation:
    """Result of a tire pressure calculation."""
    car_name: str
    weather_condition: str  # dry / wet
    weather_label: str      # Human-readable: "Dry", "Wet"
    ambient_temp: float
    track_temp: float
    pressure_gain: float    # Estimated PSI gain cold to hot
    optimal_hot_min: float
    optimal_hot_max: float
    cold_pressures: dict[str, float]   # FL, FR, RL, RR — what to set in pits
    estimated_hot: dict[str, float]    # FL, FR, RL, RR — estimated on-track PSI
    temp_status: str        # "too_hot", "optimal", "too_cold"
    temp_delta: float       # How far avg estimated hot is from the window
    notes: list[str]


def classify_weather(ambient_temp: float, is_wet: bool) -> tuple[str, str]:
    if is_wet:
        return "wet", "Wet"
    return "dry", "Dry"


def _estimate_pressure_gain(track_temp: float) -> float:
    """
    Estimate PSI gain from cold to hot based on track temperature.

    Baseline: 25°C track -> 2.3 PSI gain (calibrated from real ACC data).
    Rule: 0.1 PSI per every 2°C of track temp change from the 25°C reference.

    Examples:
        10°C  -> 1.55 PSI
        25°C  -> 2.30 PSI
        30°C  -> 2.55 PSI
        40°C  -> 3.05 PSI
        50°C  -> 3.55 PSI
        60°C  -> 4.05 PSI
    """
    gain = 2.3 + (track_temp - 25.0) * 0.05
    return round(max(gain, 1.0), 2)


def calculate_tire_recommendation(
    car_name: str,
    ambient_temp: float,
    track_temp: float,
    is_wet: bool,
    tire_split_psi: float,
    wet_cold_pressures: dict[str, float],
    optimal_hot_psi: tuple[float, float],
) -> TireRecommendation:
    """
    Calculate recommended cold starting tire pressures.

    For dry conditions cold pressures are derived dynamically:
        base_cold = hot_target - gain(track_temp)
        FL = FR = base_cold + tire_split_psi
        RL = RR = base_cold

    For wet conditions the static wet_cold_pressures from car data are used.
    """
    condition, label = classify_weather(ambient_temp, is_wet)
    hot_min, hot_max = optimal_hot_psi
    hot_target = (hot_min + hot_max) / 2.0
    notes = []

    pressure_gain = _estimate_pressure_gain(track_temp)

    if is_wet:
        cold_pressures = dict(wet_cold_pressures)
    else:
        base_cold = round(hot_target - pressure_gain, 1)
        cold_pressures = {
            "FL": round(base_cold + tire_split_psi, 1),
            "FR": round(base_cold + tire_split_psi, 1),
            "RL": base_cold,
            "RR": base_cold,
        }

    estimated_hot = {c: round(p + pressure_gain, 1) for c, p in cold_pressures.items()}
    avg_hot = sum(estimated_hot.values()) / len(estimated_hot)

    if avg_hot > hot_max:
        temp_status = "too_hot"
        temp_delta = round(avg_hot - hot_max, 1)
    elif avg_hot < hot_min:
        temp_status = "too_cold"
        temp_delta = round(hot_min - avg_hot, 1)
    else:
        temp_status = "optimal"
        temp_delta = 0.0

    notes.append(f"Estimated pressure gain (cold to hot): +{pressure_gain:.2f} PSI")
    notes.append(f"Rule: 0.1 PSI per 2°C track temp change from 25°C reference.")

    if is_wet:
        notes.append("Wet: static cold pressures applied.")
    else:
        notes.append(
            f"Cold pressures target {hot_target:.1f} PSI hot "
            f"(centre of {hot_min}-{hot_max} window)."
        )
        if track_temp >= 40:
            notes.append(
                f"High track temp ({track_temp:.0f}°C): larger gain means lower cold start."
            )

    notes.append("Fine-tune each corner with the +/- buttons based on what you see in-game.")

    return TireRecommendation(
        car_name=car_name,
        weather_condition=condition,
        weather_label=label,
        ambient_temp=ambient_temp,
        track_temp=track_temp,
        pressure_gain=pressure_gain,
        optimal_hot_min=hot_min,
        optimal_hot_max=hot_max,
        cold_pressures=cold_pressures,
        estimated_hot=estimated_hot,
        temp_status=temp_status,
        temp_delta=temp_delta,
        notes=notes,
    )
