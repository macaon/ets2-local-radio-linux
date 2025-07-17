#!/usr/bin/env python3
"""
Mathematical helper utilities for ETS2 Local Radio
"""

import math

def calculate_2d_distance(x1, z1, x2, z2):
    """Calculate 2D distance between two points using X and Z coordinates"""
    return math.sqrt((x1 - x2)**2 + (z1 - z2)**2)

def calculate_3d_distance(x1, y1, z1, x2, y2, z2):
    """Calculate 3D distance between two points"""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)

def calculate_signal_strength(distance, max_range):
    """Calculate signal strength based on distance and maximum range"""
    if distance >= max_range:
        return 0.0
    
    # Normalize distance (0 to 1)
    normalized_distance = distance / max_range
    
    # Realistic signal strength calculation with gradual falloff
    if normalized_distance < 0.2:
        return 1.0  # Full signal in close range
    elif normalized_distance < 0.5:
        return 0.9 - (normalized_distance - 0.2) * 0.3  # Good signal
    elif normalized_distance < 0.8:
        return 0.6 - (normalized_distance - 0.5) * 0.5  # Moderate signal
    else:
        return max(0.0, 0.3 - (normalized_distance - 0.8) * 1.5)  # Weak signal

def clamp(value, min_value, max_value):
    """Clamp value between min and max"""
    return max(min_value, min(value, max_value))

def normalize_value(value, min_value, max_value):
    """Normalize value to 0-1 range"""
    if max_value == min_value:
        return 0.0
    return (value - min_value) / (max_value - min_value)

def lerp(start, end, factor):
    """Linear interpolation between start and end values"""
    return start + (end - start) * clamp(factor, 0.0, 1.0)

def smooth_step(edge0, edge1, x):
    """Smooth step function for smooth transitions"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def degrees_to_radians(degrees):
    """Convert degrees to radians"""
    return degrees * math.pi / 180.0

def radians_to_degrees(radians):
    """Convert radians to degrees"""
    return radians * 180.0 / math.pi

def calculate_bearing(x1, z1, x2, z2):
    """Calculate bearing (angle) from point 1 to point 2"""
    dx = x2 - x1
    dz = z2 - z1
    angle = math.atan2(dz, dx)
    return radians_to_degrees(angle)

def is_point_in_circle(point_x, point_z, center_x, center_z, radius):
    """Check if a point is within a circular area"""
    distance = calculate_2d_distance(point_x, point_z, center_x, center_z)
    return distance <= radius

def format_distance(distance_meters):
    """Format distance for display"""
    if distance_meters < 1000:
        return f"{distance_meters:.0f}m"
    else:
        return f"{distance_meters/1000:.1f}km"

def format_coordinates(x, y, z, precision=1):
    """Format coordinates for display"""
    return f"({x:.{precision}f}, {y:.{precision}f}, {z:.{precision}f})"
