#!/usr/bin/env python3
"""
Background telemetry monitoring for ETS2 Truck Companion
"""

import threading
from config import Config


class BackgroundMonitor:
    """Background thread to monitor truck telemetry"""

    def __init__(self, coord_reader, radio_controller):
        self.coord_reader = coord_reader
        self.radio_controller = radio_controller
        self.thread = None
        self._stop_event = threading.Event()

    def start(self):
        """Start the background monitoring thread"""
        if not self.coord_reader.is_connected():
            print("Cannot start monitoring: telemetry not connected")
            return False

        if self.is_running():
            print("Background monitor already running")
            return True

        self._stop_event.clear()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("Background telemetry monitoring started")
        return True

    def stop(self):
        """Stop the background monitoring thread"""
        if not self.is_running():
            return

        self._stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        print("Background telemetry monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._stop_event.is_set():
            try:
                telemetry = self.coord_reader.read_telemetry()

                if telemetry:
                    self.radio_controller.update_telemetry(telemetry)

            except Exception as e:
                print(f"Error in telemetry monitoring: {e}")
                if self._stop_event.wait(timeout=2):
                    break
                continue

            if self._stop_event.wait(timeout=Config.UPDATE_INTERVAL):
                break

    def is_running(self):
        """Check if monitoring is running"""
        return self.thread is not None and self.thread.is_alive()
