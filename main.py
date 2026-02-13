#!/usr/bin/env python3
"""
ETS2 Truck Companion - Linux Fork
Main application entry point

Based on https://github.com/Koenvh1/ets2-local-radio/
Enhanced with dashboard, travel log, radio static, and gamepad support
"""

import signal
import sys
from config import Config
from telemetry.coordinate_reader import ETS2CoordinateReader
from data.city_database import ETS2CityDatabase
from data.station_manager import StationManager
from data.travel_log import TravelLog
from data.settings import SettingsManager
from core.radio_controller import RadioController
from core.background_monitor import BackgroundMonitor
from web.app import create_app


class ETS2CompanionApp:
    """Main ETS2 Truck Companion application"""

    def __init__(self):
        # Initialize components
        self.coord_reader = ETS2CoordinateReader()
        self.city_db = ETS2CityDatabase()
        self.station_manager = StationManager()
        self.travel_log = TravelLog(Config.TRAVEL_LOG_DB)
        self.settings_manager = SettingsManager(Config.SETTINGS_FILE)

        self.radio_controller = RadioController(
            self.city_db,
            self.station_manager,
            self.coord_reader
        )
        self.radio_controller.travel_log = self.travel_log
        self.radio_controller.settings_manager = self.settings_manager

        self.background_monitor = BackgroundMonitor(
            self.coord_reader,
            self.radio_controller
        )

        # Flask app
        self.app = create_app(self.radio_controller)

        # Setup signal handlers
        self.setup_signal_handlers()
        self.running = True

    def setup_signal_handlers(self):
        def signal_handler(signum, frame):
            print(f"\nReceived signal {signum}, shutting down...")
            self.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def initialize(self):
        print("\n" + "=" * 70)
        print("ETS2 Truck Companion - Linux Fork")
        print("=" * 70)

        telemetry_connected = self.radio_controller.initialize()

        if telemetry_connected:
            self.background_monitor.start()

        self.print_status_info(telemetry_connected)
        return True

    def print_status_info(self, telemetry_connected):
        print(f"Stations: {self.station_manager.get_total_station_count()} "
              f"across {self.station_manager.get_country_count()} countries")
        print(f"Cities: {self.city_db.get_city_count()} transmission towers")
        print(f"Plugin: {'Connected' if telemetry_connected else 'Not available'}")
        print(f"Interface: http://localhost:{Config.PORT}")
        print("=" * 70)

        if telemetry_connected:
            print("REAL-TIME TRACKING ACTIVE")
            print("  - Live dashboard with speed, fuel, RPM, gear")
            print("  - Automatic station switching based on location")
            print("  - Signal strength simulation with radio static")
            print("  - Gamepad support for station switching")
            print("  - Travel log with job history")
        else:
            print("Manual mode - telemetry plugin not detected")
            print("  - Install ETS2 telemetry plugin for full features")

        print("=" * 70)

    def run(self):
        try:
            self.app.run(
                host=Config.HOST,
                port=Config.PORT,
                debug=Config.DEBUG,
                use_reloader=False
            )
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        if not self.running:
            return

        print("\nShutting down ETS2 Truck Companion...")
        self.running = False
        self.background_monitor.stop()
        self.radio_controller.cleanup()
        print("Shutdown complete")


def main():
    try:
        app = ETS2CompanionApp()
        if app.initialize():
            app.run()
        else:
            print("Failed to initialize application")
            sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
