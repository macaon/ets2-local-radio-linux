#!/usr/bin/env python3
"""
Radio station management for ETS2 Local Radio
"""

import os
import json
import re
import random
from config import Config

class StationManager:
    """Manages radio station data loading and access"""
    
    def __init__(self, stations_file=None):
        self.stations_file = stations_file or Config.get_stations_file_path()
        self.stations = {}
        self.load_stations()
    
    def load_stations(self):
        """Load radio stations from file or remote URL"""
        # Try to load from stations.json file first
        if os.path.exists(self.stations_file):
            try:
                with open(self.stations_file, 'r') as f:
                    self.stations = json.load(f)
                print(f"✅ Loaded stations from {self.stations_file}")
                return
            except Exception as e:
                print(f"⚠️ Error loading {self.stations_file}: {e}")
        
        # Try to load from remote URL
        try:
            self._load_from_remote()
        except Exception as e:
            print(f"⚠️ Error loading stations from remote URL: {e}")
            self._create_fallback_stations()
    
    def _load_from_remote(self):
        """Load stations from remote URL"""
        import requests
        print("📡 Loading radio stations from remote URL...")
        
        response = requests.get(Config.REMOTE_STATIONS_URL, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        content = response.text
        print("🔍 Parsing stations from remote source...")
        
        # Parse the JavaScript file line by line
        self._parse_stations_from_remote(content)
    
    def _parse_stations_from_remote(self, content):
        """Parse the JavaScript file line by line to extract stations"""
        lines = content.split('\n')
        
        current_country = None
        current_stations = []
        in_station = False
        current_station = {}
        brace_count = 0
        
        processed_stations = {}
        
        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if line.startswith('//') or line.startswith('/*') or not line:
                continue

            # Look for country definition
            country_match = re.match(r'"?(\w+)"?\s*:\s*\[', line)
            if country_match:
                # Save previous country if we have one
                self._flush_country(current_country, current_stations, processed_stations)

                # Start new country
                current_country = country_match.group(1)
                current_stations = []
                continue
            
            # Look for station start
            if line.strip() == '{':
                in_station = True
                current_station = {}
                brace_count = 1
                continue
            
            # Look for station end
            if in_station and line.strip() in ['}', '},']:
                brace_count -= 1
                if brace_count == 0:
                    # Station complete
                    if self._is_valid_station(current_station):
                        # Make logo URL absolute
                        if current_station.get('logo') and not current_station['logo'].startswith('http'):
                            current_station['logo'] = f"https://localradio.koenvh.nl/{current_station['logo']}"
                        
                        # Add country field
                        current_station['country'] = current_country.title() if current_country else ''
                        current_station['city'] = ''
                        current_stations.append(current_station)
                    
                    in_station = False
                    current_station = {}
                continue
            
            # Parse station properties
            if in_station:
                # Extract name
                name_match = re.search(r'name:\s*"([^"]+)"', line)
                if name_match:
                    current_station['name'] = name_match.group(1)
                    continue
                
                # Extract logo
                logo_match = re.search(r'logo:\s*"([^"]+)"', line)
                if logo_match:
                    current_station['logo'] = logo_match.group(1)
                    continue
                
                # Extract URL
                url_match = re.search(r'url:\s*"([^"]+)"', line)
                if url_match:
                    current_station['stream_url'] = url_match.group(1)
                    continue
        
        # Don't forget the last country
        self._flush_country(current_country, current_stations, processed_stations)
        
        if processed_stations:
            self.stations = processed_stations
            total_stations = sum(len(stations) for stations in self.stations.values())
            print(f"✅ Successfully loaded {total_stations} stations for {len(self.stations)} countries from remote source")
            print(f"🌍 Available countries: {', '.join(sorted(self.stations.keys()))}")
        else:
            print("⚠️ No stations found in remote source, using fallback")
            self._create_fallback_stations()
    
    def _flush_country(self, country, stations, processed_stations):
        """Save accumulated stations for a country into processed_stations"""
        if country and stations:
            country_name = Config.COUNTRY_MAPPING.get(country.lower(), country.lower())
            if country_name and country != 'christmas':
                processed_stations[country_name] = stations
                print(f"📻 Processed {len(stations)} stations for {country} -> {country_name}")

    def _is_valid_station(self, station):
        """Check if a station has required fields and is not a placeholder"""
        if not isinstance(station, dict):
            return False
        
        name = station.get('name', '').strip()
        url = station.get('stream_url', '').strip()
        
        # Skip empty stations or placeholder entries
        if not name or not url:
            return False
        
        # Skip placeholder entries
        if 'upcoming' in name.lower() or 'grinch' in name.lower():
            return False
        
        return True
    
    def _create_fallback_stations(self):
        """Create fallback stations if remote loading fails"""
        self.stations = {
            "poland": [
                {"name": "RMF FM", "stream_url": "https://rs9-krk2-cyfronet.rmfstream.pl/RMFFM48", "country": "Poland", "logo": "", "city": "Warsaw"},
                {"name": "Radio Zet", "stream_url": "https://radiostream.pl/tuba9-1.mp3", "country": "Poland", "logo": "", "city": "Warsaw"},
                {"name": "Eska Rock", "stream_url": "https://waw02-03.ic.smcdn.pl/t032-1.mp3", "country": "Poland", "logo": "", "city": "Warsaw"}
            ],
            "germany": [
                {"name": "Antenne Bayern", "stream_url": "https://stream.antenne.de/antenne", "country": "Germany", "logo": "", "city": "Munich"},
                {"name": "Radio Hamburg", "stream_url": "https://stream.radiohamburg.de/rhh-live/mp3-128", "country": "Germany", "logo": "", "city": "Hamburg"},
                {"name": "SWR3", "stream_url": "https://liveradio.swr.de/sw282p3/swr3/", "country": "Germany", "logo": "", "city": "Stuttgart"}
            ],
            "france": [
                {"name": "RTL", "stream_url": "https://streaming.radio.rtl.fr/rtl-1-48-192", "country": "France", "logo": "", "city": "Paris"},
                {"name": "France Inter", "stream_url": "https://icecast.radiofrance.fr/franceinter-midfi.mp3", "country": "France", "logo": "", "city": "Paris"}
            ],
            "uk": [
                {"name": "BBC Radio 1", "stream_url": "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one", "country": "United Kingdom", "logo": "", "city": "London"},
                {"name": "BBC Radio 2", "stream_url": "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_two", "country": "United Kingdom", "logo": "", "city": "London"}
            ]
        }
        
        total_stations = sum(len(stations) for stations in self.stations.values())
        print(f"📻 Using fallback stations: {total_stations} stations for {len(self.stations)} countries")
    
    def get_stations_for_country(self, country):
        """Get stations for a specific country"""
        return self.stations.get(country.lower(), [])
    
    def get_random_station_for_country(self, country):
        """Get a random station for a specific country"""
        stations = self.get_stations_for_country(country)
        if stations:
            return random.choice(stations)
        return None
    
    def get_all_stations(self):
        """Get all stations"""
        return self.stations
    
    def get_countries(self):
        """Get list of all countries with stations"""
        return sorted(self.stations.keys())
    
    def get_total_station_count(self):
        """Get total number of stations"""
        return sum(len(stations) for stations in self.stations.values())
    
    def get_country_count(self):
        """Get total number of countries"""
        return len(self.stations)
    
    def reload_stations(self):
        """Reload stations from remote source"""
        try:
            self._load_from_remote()
            return True, f"Reloaded stations for {len(self.stations)} countries"
        except Exception as e:
            return False, f"Failed to reload stations: {str(e)}"
