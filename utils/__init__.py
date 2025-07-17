"""
Utility functions package
"""

from .file_helpers import (
    load_json_file, 
    save_json_file, 
    file_exists, 
    get_file_size,
    get_file_modified_time,
    ensure_directory_exists
)

from .math_helpers import (
    calculate_2d_distance,
    calculate_3d_distance,
    calculate_signal_strength,
    clamp,
    normalize_value,
    lerp,
    smooth_step,
    degrees_to_radians,
    radians_to_degrees,
    calculate_bearing,
    is_point_in_circle,
    format_distance,
    format_coordinates
)

__all__ = [
    'load_json_file', 'save_json_file', 'file_exists', 'get_file_size',
    'get_file_modified_time', 'ensure_directory_exists',
    'calculate_2d_distance', 'calculate_3d_distance', 'calculate_signal_strength',
    'clamp', 'normalize_value', 'lerp', 'smooth_step', 'degrees_to_radians',
    'radians_to_degrees', 'calculate_bearing', 'is_point_in_circle',
    'format_distance', 'format_coordinates'
]
