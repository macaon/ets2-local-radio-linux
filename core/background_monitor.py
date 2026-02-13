#!/usr/bin/env python3
"""
Background coordinate monitoring for ETS2 Local Radio
"""

import threading
from config import Config

class BackgroundMonitor:
    """Background thread to monitor truck coordinates"""

    def __init__(self, coord_reader, radio_controller):
        self.coord_reader = coord_reader
        self.radio_controller = radio_controller
        self.thread = None
        self._stop_event = threading.Event()

    def start(self):
        """Start the background monitoring thread"""
        if not self.coord_reader.is_connected():
            print("⚠️ Cannot start monitoring: telemetry not connected")
            return False

        if self.is_running():
            print("⚠️ Background monitor already running")
            return True

        self._stop_event.clear()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("🎯 Background coordinate monitoring started")
        return True

    def stop(self):
        """Stop the background monitoring thread"""
        if not self.is_running():
            return

        self._stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        print("🛑 Background coordinate monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._stop_event.is_set():
            try:
                # Read coordinates from telemetry
                coords = self.coord_reader.read_coordinates()

                if coords:
                    # Update radio controller with new position
                    self.radio_controller.update_position(coords)

            except Exception as e:
                print(f"❌ Error in coordinate monitoring: {e}")
                # Wait longer on error
                if self._stop_event.wait(timeout=2):
                    break
                continue

            # Sleep for configured interval, interruptible by stop()
            if self._stop_event.wait(timeout=Config.UPDATE_INTERVAL):
                break

    def is_running(self):
        """Check if monitoring is running"""
        return self.thread is not None and self.thread.is_alive()
