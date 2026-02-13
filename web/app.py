#!/usr/bin/env python3
"""
Flask application setup for ETS2 Truck Companion
"""

import os
from flask import Flask
from flask_cors import CORS
from config import Config


def create_app(radio_controller):
    """Create and configure Flask application"""

    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    )
    CORS(app)

    app.config.update(
        SECRET_KEY=os.urandom(24).hex(),
        DEBUG=Config.DEBUG
    )

    from web.routes import create_routes
    routes = create_routes(radio_controller)
    app.register_blueprint(routes)

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    return app
