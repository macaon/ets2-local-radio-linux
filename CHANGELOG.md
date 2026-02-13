# Changelog

## 2026-02-13 — Truck Companion Expansion

### New Features

- **Live Dashboard**: Speedometer, RPM gauge, fuel gauge, gear indicator, odometer, and truck condition bars — all rendered with CSS conic-gradient gauges
- **Expanded Telemetry**: Reads 35+ fields from ETS2 shared memory (speed, fuel, RPM, gear, damage, job info, fines, rest stops, truck brand/name, and more)
- **Job Tracking**: Detects job start/delivery events from telemetry; displays active job card with cargo, route, distance remaining, and income
- **Damage Summary**: Per-component health bars for engine, transmission, cabin, chassis, wheels, and cargo
- **Travel Log**: SQLite-backed persistent history of city visits, completed jobs, and fines with aggregate statistics
- **Radio Static / Interference**: Web Audio API procedural white noise that crossfades with the radio stream based on signal strength, with random crackle spikes
- **Gamepad Support**: Browser Gamepad API integration — D-pad left/right for station switching, up/down for volume, with debouncing
- **Audible Alerts**: Optional oscillator-based tones for speeding, low fuel, rest needed, and fines (off by default)
- **Settings Persistence**: User preferences (alerts, static, auto-switch, gamepad, dashboard) saved to `settings.json` and exposed via `/api/settings`
- **Tabbed Web UI**: Dashboard, Radio, Travel Log, and Settings tabs replace the single-page layout
- **Alert System**: Backend alert detection with 60-second cooldowns; frontend toast notifications

### API Additions

- `GET /api/telemetry` — truck state (speed, fuel, RPM, damage, job)
- `GET /api/alerts` — consume pending alerts
- `GET /api/travel/stats` — aggregate travel statistics
- `GET /api/travel/recent` — recent city visits
- `GET /api/travel/jobs` — job history
- `GET/POST /api/settings` — user preferences
- `GET /api/status` now includes `truck`, `job`, `damage`, and `alerts` keys

### Architecture Changes

- Split monolithic `web/templates.py` (785-line string constant) into proper static files: `index.html`, `main.css`, `app.js`, `dashboard.js`, `audio.js`, `gamepad.js`, `travel-log.js`
- `BackgroundMonitor` now calls `read_telemetry()` instead of `read_coordinates()` for full telemetry polling
- `RadioController` expanded with truck/job/damage/alerts state and event detection (job start/end, fines)
- New modules: `data/travel_log.py` (SQLite), `data/settings.py` (JSON)
- `config.py`: `MIN_SHM_SIZE=4305`, alert thresholds, settings/travel log paths

---

## 2026-02-13

### Bug Fixes

- Fixed signal strength going negative at edge of transmission range (`city_database.py` now delegates to `math_helpers.calculate_signal_strength` which clamps to 0.0)
- Fixed `update_position` re-triggering station suggestions every 30 seconds while parked in the same city — periodic logging no longer calls `on_city_change`
- Removed dead `mmap.seek()` call before `struct.unpack_from()` in coordinate reader
- Added shared memory size validation before reading telemetry data — prevents struct errors if the file is too small
- Replaced fragile `len(city_name) > 8` city size heuristic with an explicit `LARGE_CITIES` list (Oslo is now correctly classified as large, Felixstowe as small)

### Improvements

- Added `threading.Lock` to `RadioController` to prevent data races between the background monitor thread and Flask request threads
- `BackgroundMonitor` now uses `threading.Event.wait()` instead of `time.sleep()` — `stop()` returns immediately instead of blocking up to 2 seconds
- Flask `SECRET_KEY` is now randomly generated at startup instead of hardcoded

### Code Quality

- Eliminated duplicated signal strength and distance calculations — `city_database.py` now uses `calculate_signal_strength` and `calculate_2d_distance` from `utils/math_helpers.py`
- `city_database.py` now uses `load_json_file` from `utils/file_helpers.py` instead of hand-rolled JSON loading
- Extracted `_flush_country` helper in `station_manager.py` to deduplicate country-saving logic
- Removed unused imports (`random` in radio_controller, `os`/`json` in city_database)
