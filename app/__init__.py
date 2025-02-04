from flask import Flask
from flask_cors import CORS
from app.config import get_config
from app.api.routes.pokemon_routes import pokemon_bp
from app.api.routes.graphql_routes import graphql_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    CORS(app)

    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Register blueprints
    app.register_blueprint(pokemon_bp)
    app.register_blueprint(graphql_bp, url_prefix='/graphql')

    return app 