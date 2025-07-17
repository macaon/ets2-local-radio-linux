#!/usr/bin/env python3
"""
File helper utilities for ETS2 Local Radio
"""

import os
import json
from pathlib import Path

def load_json_file(file_path, default_value=None):
    """Load JSON file with error handling"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ File not found: {file_path}")
            return default_value
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {file_path}: {e}")
        return default_value
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return default_value

def save_json_file(file_path, data):
    """Save data to JSON file with error handling"""
    try:
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return False

def file_exists(file_path):
    """Check if file exists"""
    return os.path.exists(file_path)

def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def get_file_modified_time(file_path):
    """Get file modification time"""
    try:
        return os.path.getmtime(file_path)
    except Exception:
        return 0

def ensure_directory_exists(directory_path):
    """Ensure directory exists, create if it doesn't"""
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Error creating directory {directory_path}: {e}")
        return False
