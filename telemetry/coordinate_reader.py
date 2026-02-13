#!/usr/bin/env python3
"""
ETS2 Telemetry reader for real-time position and truck state tracking
"""

import os
import time
import mmap
import struct
from config import Config


class ETS2CoordinateReader:
    """Real-time telemetry reader using ETS2 telemetry plugin shared memory"""

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
                min_size = Config.MIN_SHM_SIZE
                if self.mm.size() < min_size:
                    print(f"Shared memory too small ({self.mm.size()} bytes, need {min_size})")
                    self.disconnect()
                    return False
                self.connected = True
                print("Connected to ETS2 telemetry plugin")
                return True
            else:
                print("ETS2 telemetry plugin not found")
                return False
        except Exception as e:
            print(f"Failed to connect to telemetry: {e}")
            return False

    def read_coordinates(self):
        """Read current truck coordinates (backward compat)"""
        if not self.connected:
            return None

        try:
            x, y, z = struct.unpack_from('<ddd', self.mm, 2200)
            return {
                'x': x,
                'y': y,
                'z': z,
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"Error reading coordinates: {e}")
            return None

    def read_telemetry(self):
        """Read all useful telemetry fields from shared memory"""
        if not self.connected:
            return None

        try:
            mm = self.mm

            def _bool(offset):
                return struct.unpack_from('<?', mm, offset)[0]

            def _int(offset):
                return struct.unpack_from('<i', mm, offset)[0]

            def _uint(offset):
                return struct.unpack_from('<I', mm, offset)[0]

            def _float(offset):
                return struct.unpack_from('<f', mm, offset)[0]

            def _double3(offset):
                return struct.unpack_from('<ddd', mm, offset)

            def _uint64(offset):
                return struct.unpack_from('<Q', mm, offset)[0]

            def _int64(offset):
                return struct.unpack_from('<q', mm, offset)[0]

            def _str(offset, size=64):
                raw = struct.unpack_from(f'<{size}s', mm, offset)[0]
                return raw.split(b'\x00', 1)[0].decode('utf-8', errors='replace')

            # Coordinates and rotation
            cx, cy, cz = _double3(2200)
            rx, ry, rz = _double3(2224)

            # Speed is in m/s from the SDK, convert to km/h
            speed_ms = _float(752)
            speed_kmh = abs(speed_ms * 3.6)

            cruise_ms = _float(808)
            cruise_kmh = abs(cruise_ms * 3.6)

            speed_limit_ms = _float(840)
            speed_limit_kmh = abs(speed_limit_ms * 3.6)

            fuel = _float(800)
            fuel_capacity = _float(704)

            return {
                'timestamp': time.time(),
                # Position
                'coordinateX': cx,
                'coordinateY': cy,
                'coordinateZ': cz,
                'rotationX': rx,
                'rotationY': ry,
                'rotationZ': rz,
                # Game state
                'paused': _bool(8),
                # Drivetrain
                'speed': speed_kmh,
                'engineRpm': _float(756),
                'gear': _int(564),
                'gearDashboard': _int(568),
                'cruiseControlSpeed': cruise_kmh,
                'speedLimit': speed_limit_kmh,
                # Fuel
                'fuel': fuel,
                'fuelCapacity': fuel_capacity,
                'fuelWarning': _bool(1515),
                # Damage / wear
                'wearEngine': _float(860),
                'wearTransmission': _float(864),
                'wearCabin': _float(868),
                'wearChassis': _float(872),
                'wearWheels': _float(876),
                'cargoDamage': _float(940),
                # Truck info
                'truckOdometer': _float(880),
                'truckBrand': _str(2364),
                'truckName': _str(2428),
                # Switches
                'parkBrake': _bool(1500),
                'electricEnabled': _bool(1510),
                'engineEnabled': _bool(1511),
                # Route / job
                'plannedDistanceKm': _uint(88),
                'routeDistance': _float(884),
                'routeTime': _float(888),
                'restStop': _int(500),
                'cargo': _str(2556),
                'cityDst': _str(2684),
                'citySrc': _str(2876),
                'compDst': _str(3004),
                'compSrc': _str(3068),
                'jobIncome': _uint64(4000),
                'onJob': _bool(4300),
                'jobFinished': _bool(4301),
                'jobDelivered': _bool(4303),
                # Fines
                'fineAmount': _int64(4208),
                'fined': _bool(4304),
            }
        except Exception as e:
            print(f"Error reading telemetry: {e}")
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
