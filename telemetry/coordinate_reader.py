#!/usr/bin/env python3
"""
ETS2 Telemetry coordinate reader for real-time position tracking
"""

import os
import time
import mmap
import struct
from config import Config

class ETS2CoordinateReader:
    """Real-time coordinate reader using ETS2 telemetry plugin"""
    
    def __init__(self, shm_path=None):
        self.shm_path = shm_path or Config.TELEMETRY_PATH
        self.shm_fd = None
        self.mm = None
        self.connected = False
        
    def connect(self):
        """Connect to the shared memory"""
        try:
            if os.path.exists(self.shm_path):
                self.shm_fd = os.open(self.shm_path, os.O_RDONLY)
                self.mm = mmap.mmap(self.shm_fd, 0, access=mmap.ACCESS_READ)
                self.connected = True
                print("✅ Connected to ETS2 telemetry plugin")
                return True
            else:
                print("❌ ETS2 telemetry plugin not found")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to telemetry: {e}")
            return False
    
    def read_coordinates(self):
        """Read current truck coordinates"""
        if not self.connected:
            return None
            
        try:
            # Read coordinates from shared memory at configured offset
            self.mm.seek(Config.COORDINATE_OFFSET)
            x, y, z = struct.unpack_from('<ddd', self.mm, Config.COORDINATE_OFFSET)
            
            # Use the corrected coordinate system (no conversion needed)
            return {
                'x': x,
                'y': y,
                'z': z,
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"❌ Error reading coordinates: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from shared memory"""
        if self.mm:
            self.mm.close()
            self.mm = None
        if self.shm_fd:
            os.close(self.shm_fd)
            self.shm_fd = None
        self.connected = False
        
    def is_connected(self):
        """Check if connected to telemetry"""
        return self.connected
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
