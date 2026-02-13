#!/usr/bin/env python3
"""
JSON-based settings persistence for ETS2 Truck Companion
"""

import json
import os
import threading


DEFAULTS = {
    'audio_alerts_enabled': False,
    'static_interference_enabled': True,
    'auto_switch_enabled': True,
    'gamepad_enabled': True,
    'dashboard_visible': True,
    'alert_cooldown_seconds': 60,
}


class SettingsManager:
    """Simple JSON file settings manager"""

    def __init__(self, settings_path):
        self.path = str(settings_path)
        self._lock = threading.Lock()
        self._settings = dict(DEFAULTS)
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                self._settings.update(data)
            except Exception as e:
                print(f"Warning: could not load settings: {e}")

    def _save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Warning: could not save settings: {e}")

    def get_all(self):
        with self._lock:
            return dict(self._settings)

    def get(self, key, default=None):
        with self._lock:
            return self._settings.get(key, default)

    def update(self, data):
        """Merge new settings values"""
        with self._lock:
            # Only accept known keys
            for key in DEFAULTS:
                if key in data:
                    self._settings[key] = data[key]
            self._save()
