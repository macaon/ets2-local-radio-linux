#!/usr/bin/env python3
"""
Main radio controller for ETS2 Local Radio
"""

import time
import random
from config import Config

class RadioController:
    """Main controller for ETS2 Radio application"""
    
    def __init__(self, city_db, station_manager, coord_reader):
        self.city_db = city_db
        self.station_manager = station_manager
        self.coord_reader = coord_reader
        
        # Application state
        self.current_country = None
        self.current_city = None
        self.current_coordinates = None
        self.current_signal_strength = 0.0
        self.current_station = None
        self.current_playing_station = None  # Track what's actually playing
        
        # State tracking
        self.last_city = None
        self.last_country = None
        self.last_announcement = 0
        self.last_suggested_station = None
        
    def initialize(self):
        """Initialize the radio controller"""
        print("🎯 Initializing radio controller...")
        
        # Try to connect to telemetry
        if self.coord_reader.connect():
            print("🎯 Real-time coordinate tracking ready")
            return True
        else:
            print("⚠️ Running without coordinate tracking")
            return False
    
    def update_position(self, coordinates):
        """Update position and handle location changes"""
        if not coordinates:
            return
        
        self.current_coordinates = coordinates
        
        # Find nearest city using X and Z coordinates
        nearest_city, distance = self.city_db.find_nearest_city(
            coordinates['x'], coordinates['z']
        )
        
        if nearest_city:
            signal_strength = self.city_db.get_signal_strength(
                coordinates['x'], coordinates['z'], nearest_city
            )
            self.current_signal_strength = signal_strength
            
            # City changed or significant signal change
            if (nearest_city != self.last_city or 
                time.time() - self.last_announcement > Config.SIGNAL_ANNOUNCEMENT_INTERVAL):
                
                print(f"📍 Near {nearest_city['realName']}, {nearest_city['country']} "
                      f"(signal: {signal_strength:.1%}, distance: {distance:.0f}m)")
                
                self.on_city_change(nearest_city, signal_strength)
                self.last_city = nearest_city
                self.last_announcement = time.time()
            
            # Country changed
            if nearest_city['country'] != self.last_country:
                self.on_country_change(nearest_city['country'])
                self.last_country = nearest_city['country']
        
        elif self.last_city:
            # Left all city ranges
            print("📡 Left all city transmission ranges")
            self.last_city = None
            self.current_city = None
            self.current_signal_strength = 0.0
    
    def on_city_change(self, city, signal_strength):
        """Handle city change with signal strength"""
        self.current_city = {
            'name': city['realName'],
            'gameName': city['gameName'],
            'country': city['country'],
            'signal_strength': signal_strength,
            'coordinates': {'x': city['x'], 'y': city['y'], 'z': city['z']},
            'range': city['range']
        }
        
        # Only suggest auto-switching if we don't have a station from this country playing
        # or if the signal is very strong (entering city center)
        should_suggest = False
        
        if signal_strength > 0.6:  # Good signal threshold
            current_country = city['country'].lower()
            
            # Check if we need to suggest a station
            if not self.current_playing_station:
                # No station playing at all
                should_suggest = True
            elif self.current_playing_station.get('country', '').lower() != current_country:
                # Playing station from different country
                should_suggest = True
            # If already playing a station from this country, don't suggest
            
            if should_suggest:
                station = self.station_manager.get_random_station_for_country(current_country)
                if station:
                    self.current_station = station
                    print(f"🎵 Suggested station: {station['name']} ({signal_strength:.1%} signal)")
        
        return self.current_city
    
    def on_country_change(self, new_country):
        """Handle country change"""
        if new_country != self.current_country:
            self.current_country = new_country
            
            stations = self.station_manager.get_stations_for_country(new_country)
            cities = self.city_db.get_cities_for_country(new_country)
            
            print(f"🌍 Country: {new_country} ({len(stations)} stations, {len(cities)} cities)")
            
        return self.current_country
    
    def set_playing_station(self, station):
        """Set the currently playing station"""
        self.current_playing_station = station
        if station:
            print(f"🎵 Now playing: {station['name']} - {station.get('country', 'Unknown')}")
    
    def get_playing_station(self):
        """Get the currently playing station"""
        return self.current_playing_station
    
    def stop_playing(self):
        """Stop playing current station"""
        if self.current_playing_station:
            print(f"⏹️ Stopped: {self.current_playing_station['name']}")
        self.current_playing_station = None
    
    def get_status(self):
        """Get complete application status"""
        return {
            'country': self.current_country,
            'city': self.current_city,
            'coordinates': self.current_coordinates,
            'signal_strength': self.current_signal_strength,
            'stations': self.station_manager.get_stations_for_country(self.current_country) if self.current_country else [],
            'all_countries': self.station_manager.get_countries(),
            'plugin_connected': self.coord_reader.is_connected(),
            'tracking_mode': 'plugin' if self.coord_reader.is_connected() else 'manual',
            'total_stations': self.station_manager.get_total_station_count(),
            'total_countries': self.station_manager.get_country_count(),
            'cities_available': self.city_db.get_city_count(),
            'suggested_station': self.current_station,  # Add suggested station for auto-switching
            'playing_station': self.current_playing_station  # Add currently playing station
        }
    
    def get_stations_for_country(self, country):
        """Get stations for a specific country"""
        stations = self.station_manager.get_stations_for_country(country)
        return {
            'country': country,
            'stations': stations,
            'count': len(stations)
        }
    
    def get_cities_for_country(self, country):
        """Get cities for a country"""
        cities = self.city_db.get_cities_for_country(country)
        return {
            'country': country,
            'cities': cities,
            'count': len(cities)
        }
    
    def get_random_station(self):
        """Get random station for current country"""
        if self.current_country:
            station = self.station_manager.get_random_station_for_country(self.current_country)
            if station:
                return {'status': 'success', 'station': station}
        
        return {'status': 'error', 'message': 'No stations available'}
    
    def reload_stations(self):
        """Reload stations from remote URL"""
        success, message = self.station_manager.reload_stations()
        return {
            'status': 'success' if success else 'error',
            'message': message
        }
    
    def get_coordinates(self):
        """Get current coordinates"""
        return self.current_coordinates
    
    def cleanup(self):
        """Clean up resources"""
        if self.coord_reader:
            self.coord_reader.disconnect()
        print("🧹 Radio controller cleaned up")
