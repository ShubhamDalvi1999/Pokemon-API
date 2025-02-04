from flask import Blueprint, jsonify
import requests

graphql_bp = Blueprint('graphql', __name__)
GRAPHQL_URL = "https://beta.pokeapi.co/graphql/v1beta"

@graphql_bp.route("/pokemon/first10", methods=["GET"])
def get_first_10_pokemon():
    """Get names and base experience of first 10 Pokemon using GraphQL"""
    query = """
    query {
        pokemon_v2_pokemon(limit: 10) {
            name
            base_experience
        }
    }
    """
    
    try:
        response = requests.post(
            GRAPHQL_URL,
            json={'query': query}
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return {"error": str(e)}, 500

@graphql_bp.route("/pokemon/first5types", methods=["GET"])
def get_first_5_pokemon_types():
    """Get names and types of first 5 Pokemon using GraphQL"""
    query = """
    query {
        pokemon_v2_pokemon(limit: 5) {
            name
            pokemon_v2_pokemontypes {
                pokemon_v2_type {
                    name
                }
            }
        }
    }
    """
    
    try:
        response = requests.post(
            GRAPHQL_URL,
            json={'query': query}
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return {"error": str(e)}, 500 