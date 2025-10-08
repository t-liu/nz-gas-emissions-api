from flask import Flask
from emissions_api.api import init_routes

def create_app(config_class='emissions_api.config.DevelopmentConfig'):
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize routes
    init_routes(app)

    return app