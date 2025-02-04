from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
from graphql_routes import graphql_bp
import os
from dotenv import load_dotenv
from db_repositories import (
    PostgresRepository, MongoDBRepository,
    BigQueryRepository, RedshiftRepository, AzureSQLRepository
)

# Load environment variables from .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
print("Current directory:", current_dir)
print("Loading .env file from:", env_path)
load_dotenv(env_path)

# Debug: Print environment variables
print("\nEnvironment variables:")
print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
print(f"BIGQUERY_DATASET: {os.getenv('BIGQUERY_DATASET')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

app = Flask(__name__)
CORS(app)

# Initialize core database repositories
db_repos = {
    'postgres': PostgresRepository(os.getenv('POSTGRES_URL')),
    'mongodb': MongoDBRepository(os.getenv('MONGODB_URL'), os.getenv('MONGODB_DB')),
    'bigquery': BigQueryRepository(os.getenv('GOOGLE_CLOUD_PROJECT'), os.getenv('BIGQUERY_DATASET'))
}

# Add Redshift if properly configured
redshift_conn = os.getenv('REDSHIFT_URL')
if redshift_conn and 'your-redshift-cluster' not in redshift_conn:
    try:
        print("Attempting to connect to Redshift...")
        db_repos['redshift'] = RedshiftRepository(redshift_conn)
        print("Successfully connected to Redshift")
    except Exception as e:
        print(f"Warning: Could not connect to Redshift: {str(e)}")
        print("Redshift will be disabled")

# Add Azure SQL if properly configured
azure_conn = os.getenv('AZURE_SQL_CONNECTION')
if azure_conn and 'YOUR_SERVER_NAME' not in azure_conn:
    try:
        print("Attempting to connect to Azure SQL...")
        db_repos['azure'] = AzureSQLRepository(azure_conn)
        print("Successfully connected to Azure SQL")
    except Exception as e:
        print(f"Warning: Could not connect to Azure SQL: {str(e)}")
        print("Azure SQL will be disabled")

# Register GraphQL blueprint
app.register_blueprint(graphql_bp, url_prefix='/graphql')

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
GRAPHQL_URL = "https://beta.pokeapi.co/graphql/v1beta"

# Cache for Pokemon names
pokemon_names_cache = None

def get_all_pokemon_names():
    """Fetch and cache all Pokemon names"""
    global pokemon_names_cache
    if pokemon_names_cache is None:
        try:
            response = requests.get(f"{POKEAPI_BASE_URL}/pokemon?limit=2000")  # Get all Pokemon
            response.raise_for_status()
            data = response.json()
            pokemon_names_cache = [pokemon['name'] for pokemon in data['results']]
            pokemon_names_cache.sort()  # Sort alphabetically
        except requests.RequestException as e:
            print(f"Error fetching Pokemon names: {e}")
            pokemon_names_cache = []
    return pokemon_names_cache

def make_api_request(endpoint):
    """Helper function to make API requests to PokeAPI"""
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}, 500

@app.route("/pokemon/<name>", methods=["GET"])
def get_pokemon_details(name):
    """Get basic details of a specific Pokemon and store in databases"""
    pokemon_data = make_api_request(f"pokemon/{name.lower()}")
    if "error" in pokemon_data:
        return pokemon_data
    
    # Store data in all configured databases
    storage_results = {}
    for db_name, repo in db_repos.items():
        try:
            repo.save_pokemon(pokemon_data)
            storage_results[db_name] = "success"
        except Exception as e:
            storage_results[db_name] = str(e)
    
    # Add storage results to the response
    pokemon_data["storage_results"] = storage_results
    return jsonify(pokemon_data)

@app.route("/pokemon/<name>/from/<database>", methods=["GET"])
def get_pokemon_from_db(name, database):
    """Get Pokemon data from a specific database"""
    if database not in db_repos:
        return {"error": f"Database {database} not supported"}, 400
    
    try:
        pokemon = db_repos[database].get_pokemon(name.lower())
        return jsonify(pokemon) if pokemon else ({"error": "Pokemon not found"}, 404)
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/pokemon/list", methods=["GET"])
def list_all_pokemon():
    """Get a list of all Pokemon names"""
    return make_api_request("pokemon?limit=100000&offset=0")

@app.route("/pokemon/type/<type_name>", methods=["GET"])
def get_pokemon_by_type(type_name):
    """Get all Pokemon of a specific type"""
    return make_api_request(f"type/{type_name.lower()}")

@app.route("/pokemon/<name>/abilities", methods=["GET"])
def get_pokemon_abilities(name):
    """Get detailed abilities information of a specific Pokemon"""
    pokemon_data = make_api_request(f"pokemon/{name.lower()}")
    if "error" in pokemon_data:
        return pokemon_data
    
    abilities_info = []
    for ability_entry in pokemon_data.get("abilities", []):
        ability_url = ability_entry.get("ability", {}).get("url")
        if ability_url:
            # Fetch detailed ability information
            try:
                ability_response = requests.get(ability_url)
                ability_response.raise_for_status()
                ability_details = ability_response.json()
                
                # Demonstrate handling missing data
                ability_info = {
                    "name": ability_details.get("name", "Unknown"),
                    "is_hidden": ability_entry.get("is_hidden", False),
                    "effect": "No effect description available",
                    "short_effect": "No short effect available",
                    "has_missing_data": False
                }
                
                # Check for missing effect entries
                effect_entries = ability_details.get("effect_entries", [])
                english_effect = next((entry for entry in effect_entries if entry.get("language", {}).get("name") == "en"), None)
                
                if english_effect:
                    ability_info["effect"] = english_effect.get("effect", ability_info["effect"])
                    ability_info["short_effect"] = english_effect.get("short_effect", ability_info["short_effect"])
                else:
                    ability_info["has_missing_data"] = True
                
                abilities_info.append(ability_info)
            except requests.RequestException:
                abilities_info.append({
                    "name": ability_entry.get("ability", {}).get("name", "Unknown"),
                    "error": "Failed to fetch ability details",
                    "has_missing_data": True
                })
    
    response = {
        "pokemon_name": name,
        "abilities": abilities_info,
        "total_abilities": len(abilities_info),
        "abilities_with_missing_data": sum(1 for ability in abilities_info if ability.get("has_missing_data", False))
    }
    
    return jsonify(response)

@app.route("/pokemon/species/<name>/evolution", methods=["GET"])
def get_evolution_chain(name):
    """Get evolution chain for a Pokemon species"""
    # First get species data
    species_data = make_api_request(f"pokemon-species/{name.lower()}")
    if "error" in species_data:
        return species_data
    
    # Extract evolution chain URL and make request
    evolution_url = species_data.get("evolution_chain", {}).get("url", "")
    if not evolution_url:
        return {"error": "Evolution chain not found"}, 404
    
    evolution_id = evolution_url.split("/")[-2]
    return make_api_request(f"evolution-chain/{evolution_id}")

@app.route("/pokemon/<name>/moves", methods=["GET"])
def get_pokemon_moves(name):
    """Get all moves of a specific Pokemon"""
    pokemon_data = make_api_request(f"pokemon/{name.lower()}")
    if "error" in pokemon_data:
        return pokemon_data
    return jsonify({"moves": pokemon_data.get("moves", [])})

@app.route("/pokemon/species/<name>/habitat", methods=["GET"])
def get_pokemon_habitat(name):
    """Get habitat information for a Pokemon"""
    species_data = make_api_request(f"pokemon-species/{name.lower()}")
    if "error" in species_data:
        return species_data
    return jsonify({"habitat": species_data.get("habitat", {})})

@app.route("/pokemon/<name>/encounters", methods=["GET"])
def get_pokemon_encounters(name):
    """Get encounter locations for a Pokemon"""
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{name.lower()}/encounters")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return {"error": str(e)}, 500

@app.route('/')
def index():
    """Serve the API interface with Pokemon names"""
    pokemon_names = get_all_pokemon_names()
    return render_template('index.html', pokemon_names=pokemon_names)

if __name__ == "__main__":
    app.run(debug=True) 