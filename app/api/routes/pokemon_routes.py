from flask import Blueprint, jsonify, render_template
from app.api.services.pokemon_service import PokemonService
from app.config import get_config
from app.database.repositories.postgres import PostgresRepository
from app.database.repositories.mongodb import MongoDBRepository
from app.database.repositories.bigquery import BigQueryRepository
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pokemon_bp = Blueprint('pokemon', __name__)

# Initialize services
config = get_config()
pokemon_service = PokemonService(config)

# Initialize repositories with error handling
db_repos = {}

def init_repository(name, repo_class, *args):
    """Initialize a repository with error handling"""
    try:
        db_repos[name] = repo_class(*args)
        logger.info(f"Successfully initialized {name} repository")
    except Exception as e:
        logger.warning(f"Failed to initialize {name} repository: {str(e)}")

# Initialize each repository separately
if config.POSTGRES_URL:
    init_repository('postgres', PostgresRepository, config.POSTGRES_URL)

if config.MONGODB_URL and config.MONGODB_DB:
    init_repository('mongodb', MongoDBRepository, config.MONGODB_URL, config.MONGODB_DB)

if config.GOOGLE_CLOUD_PROJECT and config.BIGQUERY_DATASET and config.GOOGLE_APPLICATION_CREDENTIALS:
    init_repository('bigquery', BigQueryRepository, config.GOOGLE_CLOUD_PROJECT, config.BIGQUERY_DATASET)

@pokemon_bp.route("/pokemon/<name>", methods=["GET"])
def get_pokemon_details(name):
    """Get basic details of a specific Pokemon and store in databases"""
    try:
        pokemon_data = pokemon_service.get_pokemon_details(name)
        
        # Store data in available databases
        storage_results = {}
        for db_name, repo in db_repos.items():
            try:
                repo.save_pokemon(pokemon_data)
                storage_results[db_name] = "success"
            except Exception as e:
                storage_results[db_name] = str(e)
                logger.error(f"Error storing in {db_name}: {str(e)}")
        
        # Add storage results to the response
        pokemon_data["storage_results"] = storage_results
        return jsonify(pokemon_data)
    except Exception as e:
        logger.error(f"Error getting Pokemon details: {str(e)}")
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/<name>/from/<database>", methods=["GET"])
def get_pokemon_from_db(name, database):
    """Get Pokemon data from a specific database"""
    if database not in db_repos:
        return {"error": f"Database {database} not available"}, 400
    
    try:
        pokemon = db_repos[database].get_pokemon(name.lower())
        return jsonify(pokemon) if pokemon else ({"error": "Pokemon not found"}, 404)
    except Exception as e:
        logger.error(f"Error retrieving from {database}: {str(e)}")
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/list", methods=["GET"])
def list_all_pokemon():
    """Get a list of all Pokemon names"""
    try:
        pokemon_list = pokemon_service.get_all_pokemon_names()
        return jsonify({"results": [{"name": name} for name in pokemon_list]})
    except Exception as e:
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/type/<type_name>", methods=["GET"])
def get_pokemon_by_type(type_name):
    """Get all Pokemon of a specific type"""
    try:
        return jsonify(pokemon_service.get_pokemon_by_type(type_name))
    except Exception as e:
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/<name>/abilities", methods=["GET"])
def get_pokemon_abilities(name):
    """Get detailed abilities information of a specific Pokemon"""
    try:
        return jsonify(pokemon_service.get_pokemon_abilities(name))
    except Exception as e:
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/species/<name>/evolution", methods=["GET"])
def get_evolution_chain(name):
    """Get evolution chain for a Pokemon species"""
    try:
        return jsonify(pokemon_service.get_evolution_chain(name))
    except Exception as e:
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/<name>/moves", methods=["GET"])
def get_pokemon_moves(name):
    """Get all moves of a specific Pokemon"""
    try:
        return jsonify(pokemon_service.get_pokemon_moves(name))
    except Exception as e:
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/species/<name>/habitat", methods=["GET"])
def get_pokemon_habitat(name):
    """Get habitat information for a Pokemon"""
    try:
        return jsonify(pokemon_service.get_pokemon_habitat(name))
    except Exception as e:
        return {"error": str(e)}, 500

@pokemon_bp.route("/pokemon/<name>/encounters", methods=["GET"])
def get_pokemon_encounters(name):
    """Get encounter locations for a Pokemon"""
    try:
        return jsonify(pokemon_service.get_pokemon_encounters(name))
    except Exception as e:
        return {"error": str(e)}, 500

@pokemon_bp.route('/')
def index():
    """Serve the API interface with Pokemon names"""
    try:
        pokemon_names = pokemon_service.get_all_pokemon_names()
        return render_template('pokemon/index.html', pokemon_names=pokemon_names)
    except Exception as e:
        return {"error": str(e)}, 500 