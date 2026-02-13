#!/usr/bin/env python3
"""
Configuration management for ETS2 Local Radio
"""

import os
from pathlib import Path

class Config:
    """Configuration settings for ETS2 Local Radio"""
    
    # Application settings
    APP_NAME = "ETS2 Local Radio - Linux Fork"
    VERSION = "1.0.0"
    
    # Web server settings
    HOST = os.getenv('ETS2_HOST', '0.0.0.0')
    PORT = int(os.getenv('ETS2_PORT', 5000))
    DEBUG = os.getenv('ETS2_DEBUG', 'false').lower() == 'true'
    
    # File paths
    BASE_DIR = Path(__file__).parent
    CITIES_FILE = BASE_DIR / 'cities.json'
    STATIONS_FILE = BASE_DIR / 'stations.json'
    
    # Telemetry settings
    TELEMETRY_PATH = '/dev/shm/SCS/SCSTelemetry'
    COORDINATE_OFFSET = 2200  # Memory offset for coordinates
    UPDATE_INTERVAL = 1  # Seconds between coordinate updates
    STATUS_UPDATE_INTERVAL = 2  # Seconds between status updates
    
    # Signal strength settings
    BASE_TRANSMISSION_RANGE = 25000  # Base range in meters
    MAJOR_CITY_MULTIPLIER = 2.5
    LARGE_CITY_MULTIPLIER = 1.8
    SMALL_CITY_MULTIPLIER = 1.2
    
    # Station loading settings
    REMOTE_STATIONS_URL = "https://localradio.koenvh.nl/stations/stations-europe.js"
    REQUEST_TIMEOUT = 10  # Seconds
    
    # UI settings
    SIGNAL_ANNOUNCEMENT_INTERVAL = 30  # Seconds between signal announcements (increased from 15)
    
    # Country name mapping for station parsing
    COUNTRY_MAPPING = {
        'aland': 'finland', 'denmark': 'denmark', 'finland': 'finland', 
        'iceland': 'iceland', 'norway': 'norway', 'sweden': 'sweden', 
        'austria': 'austria', 'belgium': 'belgium', 'france': 'france', 
        'germany': 'germany', 'liechtenstein': 'liechtenstein',
        'luxembourg': 'luxembourg', 'netherlands': 'netherlands', 
        'switzerland': 'switzerland', 'uk': 'uk', 'england': 'uk', 
        'scotland': 'uk', 'wales': 'uk', 'nireland': 'uk', 'belarus': 'belarus', 
        'czech': 'czechia', 'estonia': 'estonia', 'hungary': 'hungary', 
        'latvia': 'latvia', 'lithuania': 'lithuania', 'poland': 'poland', 
        'russia': 'russia', 'slovakia': 'slovakia', 'ukraine': 'ukraine', 
        'italy': 'italy', 'spain': 'spain', 'portugal': 'portugal', 
        'greece': 'greece', 'turkey': 'turkey', 'croatia': 'croatia', 
        'slovenia': 'slovenia', 'bosnia': 'bosnia', 'serbia': 'serbia', 
        'montenegro': 'montenegro', 'macedonia': 'macedonia', 'albania': 'albania', 
        'bulgaria': 'bulgaria', 'romania': 'romania', 'moldova': 'moldova', 
        'ireland': 'ireland', 'malta': 'malta', 'cyprus': 'cyprus'
    }
    
    # Major cities for increased transmission range
    MAJOR_CITIES = [
        'london', 'paris', 'berlin', 'madrid', 'rome', 'warsaw', 'prague'
    ]

    # Large cities - next tier below major
    LARGE_CITIES = [
        'oslo', 'stockholm', 'copenhagen', 'helsinki', 'vienna', 'brussels',
        'amsterdam', 'zurich', 'munich', 'hamburg', 'frankfurt', 'cologne',
        'lyon', 'marseille', 'barcelona', 'lisbon', 'milan', 'naples',
        'budapest', 'bucharest', 'sofia', 'athens', 'istanbul', 'dublin',
        'edinburgh', 'manchester', 'birmingham', 'glasgow', 'liverpool',
        'rotterdam', 'antwerp', 'gothenburg', 'malmo', 'bergen', 'krakow',
        'gdansk', 'wroclaw', 'poznan', 'bratislava', 'vilnius', 'riga',
        'tallinn', 'minsk', 'kyiv', 'zagreb', 'belgrade', 'stuttgart',
        'dortmund', 'dusseldorf', 'hannover', 'nuremberg', 'leipzig',
        'dresden', 'bremen', 'duisburg', 'essen', 'genoa', 'turin',
        'seville', 'valencia', 'porto', 'thessaloniki'
    ]
    
    @classmethod
    def get_cities_file_path(cls):
        """Get the path to the cities file"""
        return str(cls.CITIES_FILE)
    
    @classmethod
    def get_stations_file_path(cls):
        """Get the path to the stations file"""
        return str(cls.STATIONS_FILE)
    
    @classmethod
    def get_transmission_range(cls, city_name):
        """Calculate transmission range for a city"""
        city_name_lower = city_name.lower()
        
        if any(major in city_name_lower for major in cls.MAJOR_CITIES):
            return cls.BASE_TRANSMISSION_RANGE * cls.MAJOR_CITY_MULTIPLIER
        elif any(large in city_name_lower for large in cls.LARGE_CITIES):
            return cls.BASE_TRANSMISSION_RANGE * cls.LARGE_CITY_MULTIPLIER
        else:
            return cls.BASE_TRANSMISSION_RANGE * cls.SMALL_CITY_MULTIPLIER
