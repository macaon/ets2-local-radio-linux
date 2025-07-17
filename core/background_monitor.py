#!/usr/bin/env python3
"""
Background coordinate monitoring for ETS2 Local Radio
"""

import time
import threading
from config import Config

class BackgroundMonitor:
    """Background thread to monitor truck coordinates"""
    
    def __init__(self, coord_reader, radio_controller):
        self.coord_reader = coord_reader
        self.radio_controller = radio_controller
        self.thread = None
        self.running = False
        
    def start(self):
        """Start the background monitoring thread"""
        if not self.coord_reader.is_connected():
            print("⚠️ Cannot start monitoring: telemetry not connected")
            return False
        
        if self.running:
            print("⚠️ Background monitor already running")
            return True
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("🎯 Background coordinate monitoring started")
        return True
    
    def stop(self):
        """Stop the background monitoring thread"""
        if not self.running:
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        print("🛑 Background coordinate monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Read coordinates from telemetry
                coords = self.coord_reader.read_coordinates()
                
                if coords:
                    # Update radio controller with new position
                    self.radio_controller.update_position(coords)
                
                # Sleep for configured interval
                time.sleep(Config.UPDATE_INTERVAL)
                
            except Exception as e:
                print(f"❌ Error in coordinate monitoring: {e}")
                time.sleep(2)  # Wait longer on error
    
    def is_running(self):
        """Check if monitoring is running"""
        return self.running and self.thread and self.thread.is_alive()
