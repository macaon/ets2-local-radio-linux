#!/usr/bin/env python3
"""
ETS2 Local Radio - Linux Fork
Main application entry point

Based on https://github.com/Koenvh1/ets2-local-radio/
Enhanced with real-time coordinate tracking for Linux systems
"""

import signal
import sys
from config import Config
from telemetry.coordinate_reader import ETS2CoordinateReader
from data.city_database import ETS2CityDatabase
from data.station_manager import StationManager
from core.radio_controller import RadioController
from core.background_monitor import BackgroundMonitor
from web.app import create_app

class ETS2RadioApp:
    """Main ETS2 Radio application"""
    
    def __init__(self):
        # Initialize components
        self.coord_reader = ETS2CoordinateReader()
        self.city_db = ETS2CityDatabase()
        self.station_manager = StationManager()
        self.radio_controller = RadioController(
            self.city_db, 
            self.station_manager, 
            self.coord_reader
        )
        self.background_monitor = BackgroundMonitor(
            self.coord_reader, 
            self.radio_controller
        )
        
        # Flask app
        self.app = create_app(self.radio_controller)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Running state
        self.running = True
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def initialize(self):
        """Initialize the application"""
        print("\n" + "="*70)
        print("🚛 ETS2 Local Radio - Linux Fork")
        print("="*70)
        
        # Initialize radio controller
        telemetry_connected = self.radio_controller.initialize()
        
        # Start background monitoring if telemetry is available
        if telemetry_connected:
            self.background_monitor.start()
        
        # Print status information
        self.print_status_info(telemetry_connected)
        
        return True
    
    def print_status_info(self, telemetry_connected):
        """Print application status information"""
        print(f"📻 Stations: {self.station_manager.get_total_station_count()} "
              f"across {self.station_manager.get_country_count()} countries")
        print(f"📍 Cities: {self.city_db.get_city_count()} transmission towers")
        print(f"🎯 Plugin: {'✅ Connected' if telemetry_connected else '❌ Not available'}")
        print(f"🌐 Interface: http://localhost:{Config.PORT}")
        print("="*70)
        
        if telemetry_connected:
            print("🎉 REAL-TIME TRACKING ACTIVE!")
            print("   • Live coordinate tracking via telemetry plugin")
            print("   • Automatic station switching based on location")
            print("   • Signal strength simulation based on distance")
            print("   • Drive around to experience location-based radio!")
        else:
            print("⚠️ Manual mode - telemetry plugin not detected")
            print("   • Install ETS2 telemetry plugin for automatic switching")
            print("   • Manual station selection available")
        
        print("\n💡 Tips:")
        print("   • Place cities.json in the same directory for accurate city data")
        print("   • Place stations.json for custom radio stations")
        print("   • Run ETS2 with telemetry plugin for best experience")
        print("="*70)
    
    def run(self):
        """Run the application"""
        try:
            self.app.run(
                host=Config.HOST, 
                port=Config.PORT, 
                debug=Config.DEBUG,
                use_reloader=False  # Disable reloader to avoid issues with threads
            )
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        if not self.running:
            return
        
        print("\n🛑 Shutting down ETS2 Local Radio...")
        self.running = False
        
        # Stop background monitoring
        self.background_monitor.stop()
        
        # Clean up radio controller
        self.radio_controller.cleanup()
        
        print("✅ Shutdown complete")

def main():
    """Main entry point"""
    try:
        # Create and initialize application
        app = ETS2RadioApp()
        
        if app.initialize():
            # Run the application
            app.run()
        else:
            print("❌ Failed to initialize application")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
