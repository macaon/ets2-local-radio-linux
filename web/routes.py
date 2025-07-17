#!/usr/bin/env python3
"""
Flask API routes for ETS2 Local Radio web interface
"""

from flask import Blueprint, jsonify, request, render_template_string
from web.templates import HTML_TEMPLATE

def create_routes(radio_controller):
    """Create Flask routes with radio controller dependency"""
    
    routes = Blueprint('radio_routes', __name__)
    
    @routes.route('/')
    def index():
        """Main web interface"""
        return render_template_string(HTML_TEMPLATE)
    
    @routes.route('/api/status')
    def get_status():
        """Get complete application status"""
        return jsonify(radio_controller.get_status())
    
    @routes.route('/api/stations/<country>')
    def get_stations(country):
        """Get stations for a specific country"""
        return jsonify(radio_controller.get_stations_for_country(country))
    
    @routes.route('/api/cities/<country>')
    def get_cities(country):
        """Get cities for a country"""
        return jsonify(radio_controller.get_cities_for_country(country))
    
    @routes.route('/api/random_station')
    def get_random_station():
        """Get random station for current country"""
        return jsonify(radio_controller.get_random_station())
    
    @routes.route('/api/reload_stations', methods=['POST'])
    def reload_stations():
        """Reload stations from remote URL"""
        return jsonify(radio_controller.reload_stations())
    
    @routes.route('/api/coordinates')
    def get_coordinates():
        """Get current coordinates"""
        return jsonify(radio_controller.get_coordinates())
    
    @routes.route('/api/set_playing_station', methods=['POST'])
    def set_playing_station():
        """Set the currently playing station"""
        data = request.get_json()
        if data and 'station' in data:
            radio_controller.set_playing_station(data['station'])
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Invalid station data'})
    
    @routes.route('/api/stop_playing', methods=['POST'])
    def stop_playing():
        """Stop the currently playing station"""
        radio_controller.stop_playing()
        return jsonify({'status': 'success'})
    
    return routes
