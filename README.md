# ETS2 Truck Companion - Linux Fork

A Python application that turns Euro Truck Simulator 2 into a full truck companion experience on native Linux. Reads the truck's telemetry via shared memory, provides a live dashboard with speed/fuel/RPM gauges, location-aware radio with signal-based static interference, a persistent travel log, gamepad station switching, and audible alerts.

Still in development. Requires the native Linux version of ETS2 with the [scs-sdk-plugin](https://github.com/jackz314/scs-sdk-plugin). It will not work with Proton.

## Features

- **Live Dashboard**: Speedometer, RPM, fuel gauge, gear indicator, odometer, truck condition, and current job card — all updated in real-time
- **Location-based Radio**: Automatic station switching based on your truck's in-game position, with 1800+ stations across 100+ countries
- **Signal Strength Simulation**: Realistic signal falloff based on distance from cities, with city-size multipliers
- **Radio Static / Interference**: Web Audio API white noise crossfade — static fades in as signal drops, with random crackle
- **Gamepad Support**: Switch stations and control volume with a gamepad D-pad via the browser Gamepad API
- **Travel Log**: SQLite-backed history of city visits, completed jobs, and fines with aggregate statistics
- **Audible Alerts**: Optional oscillator-based tones for speeding, low fuel, rest needed, and fines (off by default)
- **Settings Persistence**: User preferences saved to JSON and applied on reload
- **Tabbed Web UI**: Dashboard, Radio, Travel Log, and Settings in a clean tabbed interface

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/macaon/ets2-local-radio-linux
cd ets2-local-radio-linux
```

2. **Create and activate venv**:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Compile and install ETS2 SDK plugin**:
```bash
# Clone and build the plugin
git clone https://github.com/jackz314/scs-sdk-plugin.git
cd scs-sdk-plugin

# Build
mkdir build && cd build
cmake .. && make

# Install to ETS2
cp *.so ~/.local/share/Steam/steamapps/common/Euro\ Truck\ Simulator\ 2/bin/linux_x64/plugins/
```

5. **Download cities data**:
   - Download `cities.json` from https://github.com/Koenvh1/ETS2-City-Coordinate-Retriever and place it in the project root directory.

## Usage

### Running the Application

```bash
source venv/bin/activate
python main.py
```

The application will start and be available at `http://localhost:5000`.

### Configuration

Environment variables:

- `ETS2_HOST`: Server host (default: `0.0.0.0`)
- `ETS2_PORT`: Server port (default: `5000`)
- `ETS2_DEBUG`: Enable debug mode (default: `false`)

### Using the Web Interface

1. Open `http://localhost:5000` in your browser
2. The **Dashboard** tab shows live truck telemetry (speed, fuel, RPM, gear, job info, damage)
3. The **Radio** tab has station selection with signal strength display
4. The **Travel Log** tab shows visit history, completed jobs, and statistics
5. The **Settings** tab lets you toggle audio alerts, radio static, auto-switching, gamepad, and dashboard visibility

### Gamepad Controls

When a gamepad is connected (shown by an indicator in the bottom-right):

- **D-pad Left/Right**: Previous/next station
- **D-pad Up/Down**: Volume up/down

## Architecture

### Core Components

- **RadioController** (`core/radio_controller.py`): Central state manager — tracks truck state, radio, jobs, alerts, and coordinates
- **BackgroundMonitor** (`core/background_monitor.py`): Daemon thread polling telemetry every 1 second
- **ETS2CoordinateReader** (`telemetry/coordinate_reader.py`): Reads 35+ telemetry fields from ETS2's shared memory via `mmap`/`struct`
- **ETS2CityDatabase** (`data/city_database.py`): City lookup and signal strength calculation
- **StationManager** (`data/station_manager.py`): Radio station loading from remote JS or local JSON
- **TravelLog** (`data/travel_log.py`): SQLite persistence for visits, jobs, fines, and sessions
- **SettingsManager** (`data/settings.py`): JSON-based user preferences

### Data Flow

```
BackgroundMonitor thread
  → ETS2CoordinateReader (shared memory, 35+ fields)
  → RadioController (state update, city detection, job/fine events, alerts)
  → Flask API (/api/status, /api/telemetry, /api/alerts, etc.)
  → Browser JS polling (dashboard.js, audio.js, gamepad.js, travel-log.js)
```

### Web UI Structure

```
web/
  templates/index.html    # Tabbed HTML (Dashboard, Radio, Travel Log, Settings)
  static/css/main.css     # All styles (gauges, cards, alerts, responsive)
  static/js/app.js        # Core logic (polling, station management, tabs)
  static/js/dashboard.js  # Gauge updates, job card, damage bars
  static/js/audio.js      # Web Audio static noise + alert oscillators
  static/js/gamepad.js    # Gamepad API integration
  static/js/travel-log.js # Travel log UI
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/status` | GET | Full state (country, city, truck, job, damage, alerts, stations) |
| `/api/telemetry` | GET | Truck telemetry only (speed, fuel, RPM, damage) |
| `/api/alerts` | GET | Consume pending alerts |
| `/api/stations/<country>` | GET | Stations for a country |
| `/api/cities/<country>` | GET | Cities for a country |
| `/api/random_station` | GET | Random station for current country |
| `/api/coordinates` | GET | Current coordinates |
| `/api/set_playing_station` | POST | Set currently playing station |
| `/api/stop_playing` | POST | Stop playback |
| `/api/reload_stations` | POST | Re-fetch station data |
| `/api/travel/stats` | GET | Aggregate travel statistics |
| `/api/travel/recent` | GET | Recent city visits |
| `/api/travel/jobs` | GET | Job history |
| `/api/settings` | GET/POST | User preferences |

## Troubleshooting

### Common Issues

1. **"ETS2 telemetry plugin not found"**
   - Install the ETS2 telemetry plugin
   - Ensure ETS2 is running with the plugin active
   - Check that `/dev/shm/SCS/SCSTelemetry` exists

2. **"No stations available"**
   - Check internet connection for remote station loading
   - Verify `stations.json` file format if using local stations
   - Try reloading stations via the web interface

3. **"Connection error"**
   - Ensure the application is running
   - Check that port 5000 is not blocked

### Debug Mode

```bash
ETS2_DEBUG=true python main.py
```

## Credits

- Original ETS2 Local Radio: https://github.com/Koenvh1/ets2-local-radio/
- Station data: https://localradio.koenvh.nl/
- ETS2 Telemetry Plugin: https://github.com/jackz314, https://github.com/RenCloud, https://github.com/nlhans
