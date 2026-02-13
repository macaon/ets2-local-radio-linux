#!/usr/bin/env python3
"""
Main application controller for ETS2 Truck Companion
"""

import time
import threading
from config import Config


class RadioController:
    """Main controller for ETS2 Truck Companion application"""

    def __init__(self, city_db, station_manager, coord_reader):
        self.city_db = city_db
        self.station_manager = station_manager
        self.coord_reader = coord_reader
        self.travel_log = None
        self.settings_manager = None

        # Radio state
        self.current_country = None
        self.current_city = None
        self.current_coordinates = None
        self.current_signal_strength = 0.0
        self.current_station = None
        self.current_playing_station = None

        # Truck state
        self.truck = {}
        self.job = {}
        self.damage = {}
        self.alerts = []

        # State tracking
        self.last_city = None
        self.last_country = None
        self.last_announcement = 0
        self.last_suggested_station = None
        self._prev_on_job = False
        self._prev_fined = False
        self._prev_job_delivered = False
        self._job_start_data = None
        self._alert_cooldowns = {}

        # Thread safety
        self._lock = threading.Lock()

    def initialize(self):
        """Initialize the controller"""
        print("Initializing radio controller...")

        if self.coord_reader.connect():
            print("Real-time coordinate tracking ready")
            if self.travel_log:
                self.travel_log.start_session()
            return True
        else:
            print("Running without coordinate tracking")
            return False

    def update_telemetry(self, telemetry):
        """Update state from full telemetry dict"""
        if not telemetry:
            return

        with self._lock:
            # Build coordinates dict for backward compat
            self.current_coordinates = {
                'x': telemetry['coordinateX'],
                'y': telemetry['coordinateY'],
                'z': telemetry['coordinateZ'],
                'timestamp': telemetry['timestamp']
            }

            # Update truck state
            self.truck = {
                'speed': telemetry['speed'],
                'engineRpm': telemetry['engineRpm'],
                'gear': telemetry['gear'],
                'gearDashboard': telemetry['gearDashboard'],
                'fuel': telemetry['fuel'],
                'fuelCapacity': telemetry['fuelCapacity'],
                'fuelWarning': telemetry['fuelWarning'],
                'cruiseControlSpeed': telemetry['cruiseControlSpeed'],
                'speedLimit': telemetry['speedLimit'],
                'odometer': telemetry['truckOdometer'],
                'brand': telemetry['truckBrand'],
                'name': telemetry['truckName'],
                'parkBrake': telemetry['parkBrake'],
                'electricEnabled': telemetry['electricEnabled'],
                'engineEnabled': telemetry['engineEnabled'],
                'paused': telemetry['paused'],
            }

            # Update damage state
            self.damage = {
                'engine': telemetry['wearEngine'],
                'transmission': telemetry['wearTransmission'],
                'cabin': telemetry['wearCabin'],
                'chassis': telemetry['wearChassis'],
                'wheels': telemetry['wearWheels'],
                'cargo': telemetry['cargoDamage'],
            }

            # Update job state
            self.job = {
                'active': telemetry['onJob'],
                'finished': telemetry['jobFinished'],
                'delivered': telemetry['jobDelivered'],
                'cargo': telemetry['cargo'],
                'citySrc': telemetry['citySrc'],
                'cityDst': telemetry['cityDst'],
                'compSrc': telemetry['compSrc'],
                'compDst': telemetry['compDst'],
                'income': telemetry['jobIncome'],
                'plannedDistanceKm': telemetry['plannedDistanceKm'],
                'routeDistance': telemetry['routeDistance'],
                'routeTime': telemetry['routeTime'],
            }

            # Detect job events
            self._detect_job_events(telemetry)

            # Detect fines
            self._detect_fines(telemetry)

            # Check alert conditions
            self._check_alerts(telemetry)

        # Position/radio logic (calls _lock internally via existing methods)
        self._update_position_from_telemetry(telemetry)

    def _update_position_from_telemetry(self, telemetry):
        """Handle position/radio logic from telemetry data"""
        coordinates = {
            'x': telemetry['coordinateX'],
            'y': telemetry['coordinateY'],
            'z': telemetry['coordinateZ'],
            'timestamp': telemetry['timestamp']
        }
        self.update_position(coordinates)

    def update_position(self, coordinates):
        """Update position and handle location changes"""
        if not coordinates:
            return

        with self._lock:
            self.current_coordinates = coordinates

            nearest_city, distance = self.city_db.find_nearest_city(
                coordinates['x'], coordinates['z']
            )

            if nearest_city:
                signal_strength = self.city_db.get_signal_strength(
                    coordinates['x'], coordinates['z'], nearest_city
                )
                self.current_signal_strength = signal_strength

                city_changed = nearest_city != self.last_city

                if city_changed:
                    print(f"Near {nearest_city['realName']}, {nearest_city['country']} "
                          f"(signal: {signal_strength:.1%}, distance: {distance:.0f}m)")
                    self._on_city_change(nearest_city, signal_strength)
                    self.last_city = nearest_city
                    self.last_announcement = time.time()
                elif time.time() - self.last_announcement > Config.SIGNAL_ANNOUNCEMENT_INTERVAL:
                    print(f"Near {nearest_city['realName']}, {nearest_city['country']} "
                          f"(signal: {signal_strength:.1%}, distance: {distance:.0f}m)")
                    self._update_city_info(nearest_city, signal_strength)
                    self.last_announcement = time.time()

                if nearest_city['country'] != self.last_country:
                    self._on_country_change(nearest_city['country'])
                    self.last_country = nearest_city['country']

            elif self.last_city:
                print("Left all city transmission ranges")
                self.last_city = None
                self.current_city = None
                self.current_signal_strength = 0.0

    def _update_city_info(self, city, signal_strength):
        """Update current city info without triggering station suggestions"""
        self.current_city = {
            'name': city['realName'],
            'gameName': city['gameName'],
            'country': city['country'],
            'signal_strength': signal_strength,
            'coordinates': {'x': city['x'], 'y': city['y'], 'z': city['z']},
            'range': city['range']
        }

    def _on_city_change(self, city, signal_strength):
        """Handle city change with signal strength"""
        self._update_city_info(city, signal_strength)

        # Record visit in travel log
        if self.travel_log:
            self.travel_log.record_visit(
                city['realName'], city['country'],
                city['x'], city['z'], signal_strength
            )

        should_suggest = False
        if signal_strength > 0.6:
            current_country = city['country'].lower()
            if not self.current_playing_station:
                should_suggest = True
            elif self.current_playing_station.get('country', '').lower() != current_country:
                should_suggest = True

            if should_suggest:
                station = self.station_manager.get_random_station_for_country(current_country)
                if station:
                    self.current_station = station
                    print(f"Suggested station: {station['name']} ({signal_strength:.1%} signal)")

    def _on_country_change(self, new_country):
        """Handle country change"""
        if new_country != self.current_country:
            self.current_country = new_country
            stations = self.station_manager.get_stations_for_country(new_country)
            cities = self.city_db.get_cities_for_country(new_country)
            print(f"Country: {new_country} ({len(stations)} stations, {len(cities)} cities)")

    def _detect_job_events(self, telemetry):
        """Detect job start/end transitions"""
        on_job = telemetry['onJob']
        delivered = telemetry['jobDelivered']

        # Job started
        if on_job and not self._prev_on_job:
            print(f"Job started: {telemetry['cargo']} from {telemetry['citySrc']} to {telemetry['cityDst']}")
            self._job_start_data = {
                'cargo': telemetry['cargo'],
                'citySrc': telemetry['citySrc'],
                'compSrc': telemetry['compSrc'],
                'cityDst': telemetry['cityDst'],
                'compDst': telemetry['compDst'],
                'distance': telemetry['plannedDistanceKm'],
                'income': telemetry['jobIncome'],
            }
            if self.travel_log:
                self.travel_log.record_job_start(
                    telemetry['cargo'],
                    telemetry['citySrc'], telemetry['compSrc'],
                    telemetry['cityDst'], telemetry['compDst'],
                    telemetry['plannedDistanceKm'], telemetry['jobIncome']
                )

        # Job delivered
        if delivered and not self._prev_job_delivered:
            print(f"Job delivered! Cargo damage: {telemetry['cargoDamage']:.1%}")
            if self.travel_log:
                self.travel_log.record_job_complete(telemetry['cargoDamage'])

        self._prev_on_job = on_job
        self._prev_job_delivered = delivered

    def _detect_fines(self, telemetry):
        """Detect fine events"""
        if telemetry['fined'] and not self._prev_fined:
            amount = telemetry['fineAmount']
            city = self.current_city['name'] if self.current_city else 'Unknown'
            country = self.current_country or 'Unknown'
            print(f"Fined! Amount: {amount} in {city}, {country}")
            self._add_alert('fine', f"Fined {amount} in {city}")
            if self.travel_log:
                self.travel_log.record_fine(amount, city, country)
        self._prev_fined = telemetry['fined']

    def _check_alerts(self, telemetry):
        """Check for alert conditions"""
        now = time.time()
        cooldown = Config.ALERT_COOLDOWN_SECONDS

        # Speeding
        if (telemetry['speedLimit'] > 0 and
                telemetry['speed'] > telemetry['speedLimit'] + 5):
            self._add_alert_with_cooldown(
                'speed',
                f"Speeding! {telemetry['speed']:.0f} km/h in a {telemetry['speedLimit']:.0f} km/h zone",
                now, cooldown
            )

        # Low fuel
        if (telemetry['fuelCapacity'] > 0 and
                telemetry['fuel'] / telemetry['fuelCapacity'] < Config.LOW_FUEL_THRESHOLD and
                telemetry['engineEnabled']):
            pct = telemetry['fuel'] / telemetry['fuelCapacity'] * 100
            self._add_alert_with_cooldown(
                'fuel',
                f"Low fuel! {pct:.0f}% remaining",
                now, cooldown
            )

        # Rest needed
        if telemetry['restStop'] > 0:
            self._add_alert_with_cooldown(
                'rest',
                "Rest stop needed soon",
                now, cooldown
            )

    def _add_alert_with_cooldown(self, alert_type, message, now, cooldown):
        """Add an alert if not on cooldown"""
        last = self._alert_cooldowns.get(alert_type, 0)
        if now - last >= cooldown:
            self._add_alert(alert_type, message)
            self._alert_cooldowns[alert_type] = now

    def _add_alert(self, alert_type, message):
        """Add an alert to the pending list"""
        self.alerts.append({
            'type': alert_type,
            'message': message,
            'timestamp': time.time()
        })

    def consume_alerts(self):
        """Return and clear pending alerts"""
        with self._lock:
            alerts = list(self.alerts)
            self.alerts.clear()
            return alerts

    def set_playing_station(self, station):
        """Set the currently playing station"""
        with self._lock:
            self.current_playing_station = station
        if station:
            print(f"Now playing: {station['name']} - {station.get('country', 'Unknown')}")

    def get_playing_station(self):
        """Get the currently playing station"""
        with self._lock:
            return self.current_playing_station

    def stop_playing(self):
        """Stop playing current station"""
        with self._lock:
            if self.current_playing_station:
                print(f"Stopped: {self.current_playing_station['name']}")
            self.current_playing_station = None

    def get_status(self):
        """Get complete application status"""
        with self._lock:
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
                'suggested_station': self.current_station,
                'playing_station': self.current_playing_station,
                'truck': self.truck,
                'job': self.job,
                'damage': self.damage,
                'alerts': list(self.alerts),
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
        with self._lock:
            country = self.current_country
        if country:
            station = self.station_manager.get_random_station_for_country(country)
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
        with self._lock:
            return self.current_coordinates

    def cleanup(self):
        """Clean up resources"""
        if self.travel_log:
            # Build session stats
            stats = {}
            if self.travel_log:
                stats = self.travel_log.get_stats()
            self.travel_log.end_session(stats)
        if self.coord_reader:
            self.coord_reader.disconnect()
        print("Controller cleaned up")
