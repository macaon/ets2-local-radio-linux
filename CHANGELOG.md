# Changelog

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
