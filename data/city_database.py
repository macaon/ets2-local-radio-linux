#!/usr/bin/env python3
"""
City database management for ETS2 Local Radio
"""

from config import Config
from utils.math_helpers import calculate_2d_distance, calculate_signal_strength
from utils.file_helpers import load_json_file

class ETS2CityDatabase:
    """City database using the official cities.json format"""
    
    def __init__(self, cities_file=None):
        self.cities_file = cities_file or Config.get_cities_file_path()
        self.cities = []
        self.cities_by_country = {}
        self.load_cities()
    
    def load_cities(self):
        """Load cities from the cities.json file"""
        data = load_json_file(self.cities_file)
        if data:
            self.cities = data.get('citiesList', [])
            print(f"✅ Loaded cities from {self.cities_file}")
        else:
            print(f"⚠️ Cities file not available, using built-in data")
            self.cities = self._get_fallback_cities()

        # Process cities and group by country
        self._process_cities()

        print(f"✅ Processed {len(self.cities)} cities from {len(self.cities_by_country)} countries")
    
    def _process_cities(self):
        """Process city data and group by country"""
        for city in self.cities:
            # Convert coordinates to float
            city['x'] = float(city['x'])
            city['y'] = float(city['y'])
            city['z'] = float(city['z'])
            
            # Calculate transmission range based on city size/importance
            city['range'] = Config.get_transmission_range(city['realName'])
            
            # Group by country
            country = city['country'].lower()
            if country not in self.cities_by_country:
                self.cities_by_country[country] = []
            self.cities_by_country[country].append(city)
    
    def _get_fallback_cities(self):
        """Fallback city data if cities.json is not available"""
        return [
            {
                "gameName": "berlin",
                "realName": "Berlin",
                "country": "germany",
                "x": "18600.0",
                "y": "46.0",
                "z": "-27500.0"
            },
            {
                "gameName": "paris",
                "realName": "Paris",
                "country": "france",
                "x": "8500.0",
                "y": "45.0",
                "z": "-25200.0"
            },
            {
                "gameName": "london",
                "realName": "London",
                "country": "uk",
                "x": "5200.0",
                "y": "44.0",
                "z": "-29800.0"
            }
        ]
    
    def find_nearest_city(self, truck_x, truck_z):
        """Find the nearest city within transmission range"""
        nearest_city = None
        min_distance = float('inf')

        for city in self.cities:
            distance = calculate_2d_distance(truck_x, truck_z, city['x'], city['z'])

            # Check if within transmission range and closer than previous
            if distance <= city['range'] and distance < min_distance:
                min_distance = distance
                nearest_city = city

        return nearest_city, min_distance if nearest_city else None

    def get_signal_strength(self, truck_x, truck_z, city):
        """Calculate signal strength based on distance"""
        if not city:
            return 0.0
        distance = calculate_2d_distance(truck_x, truck_z, city['x'], city['z'])
        return calculate_signal_strength(distance, city['range'])
    
    def get_cities_for_country(self, country):
        """Get all cities for a specific country"""
        return self.cities_by_country.get(country.lower(), [])
    
    def get_all_cities(self):
        """Get all cities"""
        return self.cities
    
    def get_countries(self):
        """Get list of all countries"""
        return sorted(self.cities_by_country.keys())
    
    def get_city_count(self):
        """Get total number of cities"""
        return len(self.cities)
    
    def get_country_count(self):
        """Get total number of countries"""
        return len(self.cities_by_country)
