#!/usr/bin/env python3
"""
Flask API routes for ETS2 Truck Companion web interface
"""

from flask import Blueprint, jsonify, request, render_template


def create_routes(radio_controller):
    """Create Flask routes with radio controller dependency"""

    routes = Blueprint('radio_routes', __name__)

    # ---- Pages ----

    @routes.route('/')
    def index():
        return render_template('index.html')

    # ---- Existing API ----

    @routes.route('/api/status')
    def get_status():
        return jsonify(radio_controller.get_status())

    @routes.route('/api/stations/<country>')
    def get_stations(country):
        return jsonify(radio_controller.get_stations_for_country(country))

    @routes.route('/api/cities/<country>')
    def get_cities(country):
        return jsonify(radio_controller.get_cities_for_country(country))

    @routes.route('/api/random_station')
    def get_random_station():
        return jsonify(radio_controller.get_random_station())

    @routes.route('/api/reload_stations', methods=['POST'])
    def reload_stations():
        return jsonify(radio_controller.reload_stations())

    @routes.route('/api/coordinates')
    def get_coordinates():
        return jsonify(radio_controller.get_coordinates())

    @routes.route('/api/set_playing_station', methods=['POST'])
    def set_playing_station():
        data = request.get_json()
        if data and 'station' in data:
            radio_controller.set_playing_station(data['station'])
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Invalid station data'})

    @routes.route('/api/stop_playing', methods=['POST'])
    def stop_playing():
        radio_controller.stop_playing()
        return jsonify({'status': 'success'})

    # ---- New API endpoints ----

    @routes.route('/api/telemetry')
    def get_telemetry():
        """Full truck state"""
        status = radio_controller.get_status()
        return jsonify({
            'truck': status.get('truck', {}),
            'job': status.get('job', {}),
            'damage': status.get('damage', {}),
            'coordinates': status.get('coordinates'),
            'signal_strength': status.get('signal_strength', 0),
        })

    @routes.route('/api/alerts')
    def get_alerts():
        """Consume pending alerts"""
        return jsonify(radio_controller.consume_alerts())

    @routes.route('/api/travel/stats')
    def get_travel_stats():
        if radio_controller.travel_log:
            return jsonify(radio_controller.travel_log.get_stats())
        return jsonify({
            'total_distance': 0, 'cities_visited': 0,
            'jobs_completed': 0, 'total_income': 0, 'total_fines': 0
        })

    @routes.route('/api/travel/recent')
    def get_travel_recent():
        if radio_controller.travel_log:
            return jsonify(radio_controller.travel_log.get_recent_visits())
        return jsonify([])

    @routes.route('/api/travel/jobs')
    def get_travel_jobs():
        if radio_controller.travel_log:
            return jsonify(radio_controller.travel_log.get_job_history())
        return jsonify([])

    @routes.route('/api/settings', methods=['GET', 'POST'])
    def handle_settings():
        if not radio_controller.settings_manager:
            # Return defaults if no settings manager
            defaults = {
                'audio_alerts_enabled': False,
                'static_interference_enabled': True,
                'auto_switch_enabled': True,
                'gamepad_enabled': True,
                'dashboard_visible': True,
                'alert_cooldown_seconds': 60,
            }
            if request.method == 'POST':
                return jsonify({'status': 'success'})
            return jsonify(defaults)

        if request.method == 'POST':
            data = request.get_json()
            if data:
                radio_controller.settings_manager.update(data)
                return jsonify({'status': 'success'})
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

        return jsonify(radio_controller.settings_manager.get_all())

    return routes
