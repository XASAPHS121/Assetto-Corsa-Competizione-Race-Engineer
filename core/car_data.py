"""
ACC Race Engineer — Car Data Loader
Loads and provides access to car specifications from JSON data.
"""

import json
import os
from typing import Optional


class CarDatabase:
    """Manages car data for the ACC Race Engineer."""

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            from core.paths import get_data_path
            data_path = get_data_path("cars.json")

        with open(data_path, "r", encoding="utf-8") as f:
            self._raw = json.load(f)

        self._cars = {}
        for class_key, car_list in self._raw.items():
            for car in car_list:
                self._cars[car["name"]] = car

    @property
    def classes(self) -> list[str]:
        """Return available car classes."""
        return list(self._raw.keys())

    def get_cars_by_class(self, car_class: str) -> list[dict]:
        """Return all cars for a given class key (e.g. 'gt3')."""
        return self._raw.get(car_class, [])

    def get_car(self, name: str) -> Optional[dict]:
        """Return car data by exact name."""
        return self._cars.get(name)

    def get_all_car_names(self) -> list[str]:
        """Return a sorted list of all car names."""
        return sorted(self._cars.keys())

    def get_fuel_tank(self, name: str) -> float:
        """Return fuel tank capacity in liters for a car."""
        car = self._cars.get(name)
        if car:
            return car["fuel_tank_liters"]
        return 0.0

    def get_tire_split(self, name: str) -> float:
        """Return the front-over-rear cold PSI offset for this car (e.g. 0.2)."""
        car = self._cars.get(name)
        if car:
            return car.get("tire_split_psi", 0.2)
        return 0.2

    def get_wet_cold_pressures(self, name: str) -> dict:
        """Return static cold pressures used in wet conditions."""
        car = self._cars.get(name)
        if car:
            return car.get("wet_cold_pressures", {"FL": 27.0, "FR": 27.0, "RL": 27.0, "RR": 27.0})
        return {"FL": 27.0, "FR": 27.0, "RL": 27.0, "RR": 27.0}

    def get_optimal_hot_psi(self, name: str) -> tuple[float, float]:
        """Return (min, max) optimal hot tire pressure in PSI."""
        car = self._cars.get(name)
        if car:
            psi = car.get("optimal_hot_psi", {})
            return (psi.get("min", 26.6), psi.get("max", 27.0))
        return (26.6, 27.0)
