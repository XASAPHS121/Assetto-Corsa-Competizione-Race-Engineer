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
- Adjusts for weather conditions: Dry Hot (>30C), Dry Mild (15-30C), Dry Cold (<15C), Wet
- Shows estimated **pressure gain** from cold to hot
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
3. Hit **Calculate Pressures** to get:
   - Recommended cold pressures per corner
   - Weather classification and estimated pressure gain
   - Hot pressure status (in window / over / under)
4. Use **+/-** buttons to fine-tune each corner by 0.1 PSI increments

### Tire Pressure Physics
Cold tires in the pits have lower pressure. After a few laps on track, heat builds up and pressure rises.
The advisor calculates what cold pressure to set so that hot pressure lands in the **26.6 - 27.0 PSI** optimal window.
Hotter conditions = lower cold pressure (tires gain more heat). Colder conditions = higher cold pressure.

---

## Adding Cars

Edit `data/cars.json` to add new cars. Each entry follows this structure:

```json
{
  "name": "Car Name",
  "class": "GT3",
  "fuel_tank_liters": 120,
  "optimal_hot_psi": { "min": 26.6, "max": 27.0 },
  "cold_pressures": {
    "dry_hot":  { "FL": 24.0, "FR": 24.0, "RL": 23.8, "RR": 23.8 },
    "dry_mild": { "FL": 24.8, "FR": 24.8, "RL": 24.6, "RR": 24.6 },
    "dry_cold": { "FL": 25.6, "FR": 25.6, "RL": 25.4, "RR": 25.4 },
    "wet":      { "FL": 27.0, "FR": 27.0, "RL": 27.0, "RR": 27.0 }
  }
}
```

| Field | Description |
|-------|-------------|
| `name` | Car display name |
| `class` | `GT3` or `GT4` |
| `fuel_tank_liters` | Fuel tank capacity in liters |
| `optimal_hot_psi` | Target hot pressure range on track |
| `cold_pressures` | Starting pressures set in pits per weather condition |
| `FL, FR, RL, RR` | Front-Left, Front-Right, Rear-Left, Rear-Right |

**Weather conditions:**
| Condition | Ambient Temp | Notes |
|-----------|-------------|-------|
| `dry_hot` | > 30 C | Lower cold PSI — tires gain more heat |
| `dry_mild` | 15 - 30 C | Standard baseline |
| `dry_cold` | < 15 C | Higher cold PSI — tires gain less heat |
| `wet` | Any (rain) | Typically 27.0 PSI all around |

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
