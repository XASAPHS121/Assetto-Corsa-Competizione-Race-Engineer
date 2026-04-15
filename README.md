# Assetto Corsa Competizione Race Engineer

A desktop race engineer tool for **Assetto Corsa Competizione**, built with Python and PyQt6.
Provides fuel strategy calculations and tire pressure recommendations to help you prepare for races.

---

## Features

### Fuel Calculator
- Select any **GT3** or **GT4** car with accurate tank capacities
- Choose between **Fixed Laps** or **Timed Race** modes
- Lap time input in **minutes and seconds** for timed races
- Calculates total fuel needed, laps per full tank, and pit stops required
- Accounts for **formation lap** fuel consumption and **safety margin**
- Generates a detailed **stint breakdown table** showing fuel load and usage per stint
- PIT / FINISH badges for quick strategy overview

### Tire Advisor
- Recommends **cold starting pressures** (set in pits) per tire corner (FL, FR, RL, RR)
- Targets the optimal hot pressure window of **26.6 - 27.0 PSI**
- **Dynamic formula** — cold pressures computed directly from track temperature, not static lookup tables
- Rule: **0.1 PSI per every 2°C** of track temperature change (works correctly at 40°C+)
- Enter your **current hot PSI** from the in-game MFD to see per-corner adjustment deltas
- Per-corner **+/- adjustment buttons** with delta tracking from base recommendation
- Advisor notes with tips based on current conditions

---

## Supported Cars

### GT3 (13 cars)
Aston Martin V8 Vantage GT3, Audi R8 LMS GT3 Evo II, Bentley Continental GT3 (2018),
BMW M4 GT3, BMW M6 GT3, Ferrari 296 GT3, Ferrari 488 GT3 Evo, Honda NSX GT3 Evo,
Lamborghini Huracan GT3 Evo 2, McLaren 720S GT3 Evo, Mercedes-AMG GT3 (2020),
Nissan GT-R Nismo GT3 (2018), Porsche 911 GT3 R (992)
More coming soon...

### GT4 (6 cars)
Alpine A110 GT4, Aston Martin V8 Vantage GT4, BMW M4 GT4,
Chevrolet Camaro GT4.R, Mercedes-AMG GT4, Porsche 718 Cayman GT4 MR

---

## Installation

### Requirements
- Python 3.11+
- Windows 10/11

### Setup

```bash
# Clone or download the project
cd "C:\ACC APP\acc-engineer"

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
# Activate the virtual environment
venv\Scripts\activate

# Run the app
python main.py
```

### Development Mode (hot-reload)

```bash
python dev.py
```

This watches `ui/`, `core/`, and `data/` folders for changes and automatically restarts the app.

---

## Project Structure

```
acc-engineer/
├── main.py                  # App entry point
├── dev.py                   # Hot-reload development script
├── requirements.txt         # Python dependencies
│
├── core/                    # Backend logic
│   ├── car_data.py          # Car database loader (reads cars.json)
│   ├── fuel_calculator.py   # Fuel strategy calculation engine
│   └── tire_advisor.py      # Tire pressure recommendation engine
│
├── data/
│   └── cars.json            # Car database (tank sizes, tire pressures)
│
├── ui/                      # PyQt6 interface
│   ├── main_window.py       # Main window with header and tab navigation
│   ├── fuel_tab.py          # Fuel Calculator tab
│   ├── tire_tab.py          # Tire Advisor tab
│   └── theme.py             # Dark racing QSS theme (fully documented)
│
├── assets/                  # Icons and images
│   ├── app_icon.ico         # Window icon
│   └── arrow-*.svg/.png     # UI arrow icons for dropdowns and spinboxes
│
└── designer/                # Qt Designer .ui files (reference only)
    ├── main_window.ui
    ├── fuel_tab.ui
    └── tire_tab.ui
```

---

## How It Works

### Fuel Calculator
1. Select your car (auto-fills tank capacity)
2. Set race mode (fixed laps or timed)
3. Enter average fuel per lap, formation laps, and safety margin
4. Hit **Calculate Strategy** to get:
   - Total fuel, laps per tank, pit stops needed
   - Fuel per stop, formation fuel, fuel remaining at finish
   - Full stint breakdown with fuel loads

### Tire Advisor
1. Select your car
2. Set track condition (Dry/Wet), ambient temperature, and track temperature
3. Optionally enter your **current hot PSI** per corner (what you see in-game while on track)
4. Hit **Calculate Pressures** to get:
   - Recommended cold pressures per corner
   - Estimated pressure gain and delta vs your current setup
   - Hot pressure status (in window / over / under)
5. Use **+/-** buttons to fine-tune each corner by 0.1 PSI based on what you see in-game

### Tire Pressure Physics
Cold tires in the pits have lower pressure. After a few laps on track, heat builds up and pressure rises.
The advisor computes cold pressure dynamically using the rule: **0.1 PSI per every 2°C of track temperature**.
At 25°C track the baseline gain is 2.3 PSI. At 40°C it becomes 3.05 PSI, at 50°C it's 3.55 PSI.
The formula works at any temperature — no buckets, no static tables.
The +/- buttons exist because track layout, fuel load, and driving style all affect real-world gain.

---

## Adding Cars

Edit `data/cars.json` to add new cars. Each entry follows this structure:

```json
{
  "name": "Car Name",
  "class": "GT3",
  "fuel_tank_liters": 120,
  "optimal_hot_psi": { "min": 26.6, "max": 27.0 },
  "tire_split_psi": 0.2,
  "wet_cold_pressures": { "FL": 27.0, "FR": 27.0, "RL": 27.0, "RR": 27.0 }
}
```

| Field | Description |
|-------|-------------|
| `name` | Car display name |
| `class` | `GT3` or `GT4` |
| `fuel_tank_liters` | Fuel tank capacity in liters |
| `optimal_hot_psi` | Target hot pressure range on track |
| `tire_split_psi` | How much higher fronts run vs rears (typically 0.2 or 0.3) |
| `wet_cold_pressures` | Static cold pressures used in wet conditions |

Dry cold pressures are **not stored** — they are computed dynamically from track temperature at runtime.

---

## Tech Stack

- **Python 3.11+** with virtual environment
- **PyQt6** for the desktop UI
- **QSS** (Qt Style Sheets) for the dark racing theme
- **Pillow** for icon generation
- **watchdog** for hot-reload during development

---

## License

Personal use — built for sim racing strategy.
