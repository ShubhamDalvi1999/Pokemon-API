import requests
from typing import Dict, List, Optional
from functools import lru_cache
from app.config import Config

class PokemonService:
    """Service layer for Pokemon operations"""
    
    def __init__(self, config: Config):
        self.base_url = config.POKEAPI_BASE_URL
        self._pokemon_names_cache = None

    def get_pokemon_details(self, name: str) -> Dict:
        """Get detailed information about a specific Pokemon"""
        try:
            response = requests.get(f"{self.base_url}/pokemon/{name.lower()}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise PokemonServiceError(f"Error fetching Pokemon details: {str(e)}")

    @lru_cache(maxsize=1)
    def get_all_pokemon_names(self) -> List[str]:
        """Get a list of all Pokemon names (cached)"""
        try:
            response = requests.get(f"{self.base_url}/pokemon?limit=2000")
            response.raise_for_status()
            data = response.json()
            names = [pokemon['name'] for pokemon in data['results']]
            return sorted(names)
        except requests.RequestException as e:
            raise PokemonServiceError(f"Error fetching Pokemon list: {str(e)}")

    def get_pokemon_by_type(self, type_name: str) -> Dict:
        """Get all Pokemon of a specific type"""
        try:
            response = requests.get(f"{self.base_url}/type/{type_name.lower()}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise PokemonServiceError(f"Error fetching Pokemon by type: {str(e)}")

    def get_pokemon_abilities(self, name: str) -> Dict:
        """Get detailed ability information for a Pokemon"""
        pokemon_data = self.get_pokemon_details(name)
        abilities_info = []

        for ability_entry in pokemon_data.get("abilities", []):
            ability_url = ability_entry.get("ability", {}).get("url")
            if ability_url:
                try:
                    response = requests.get(ability_url)
                    response.raise_for_status()
                    ability_details = response.json()
                    
                    ability_info = {
                        "name": ability_details.get("name", "Unknown"),
                        "is_hidden": ability_entry.get("is_hidden", False),
                        "effect": "No effect description available",
                        "short_effect": "No short effect available",
                        "has_missing_data": False
                    }
                    
                    effect_entries = ability_details.get("effect_entries", [])
                    english_effect = next(
                        (entry for entry in effect_entries 
                         if entry.get("language", {}).get("name") == "en"),
                        None
                    )
                    
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

        return {
            "pokemon_name": name,
            "abilities": abilities_info,
            "total_abilities": len(abilities_info),
            "abilities_with_missing_data": sum(1 for ability in abilities_info if ability.get("has_missing_data", False))
        }

    def get_evolution_chain(self, name: str) -> Dict:
        """Get evolution chain for a Pokemon species"""
        try:
            # First get species data
            species_response = requests.get(f"{self.base_url}/pokemon-species/{name.lower()}")
            species_response.raise_for_status()
            species_data = species_response.json()
            
            # Extract evolution chain URL
            evolution_url = species_data.get("evolution_chain", {}).get("url", "")
            if not evolution_url:
                raise PokemonServiceError("Evolution chain not found")
            
            # Get evolution chain data
            evolution_response = requests.get(evolution_url)
            evolution_response.raise_for_status()
            return evolution_response.json()
        except requests.RequestException as e:
            raise PokemonServiceError(f"Error fetching evolution chain: {str(e)}")

    def get_pokemon_moves(self, name: str) -> Dict:
        """Get all moves of a Pokemon"""
        pokemon_data = self.get_pokemon_details(name)
        return {"moves": pokemon_data.get("moves", [])}

    def get_pokemon_habitat(self, name: str) -> Dict:
        """Get habitat information for a Pokemon"""
        try:
            response = requests.get(f"{self.base_url}/pokemon-species/{name.lower()}")
            response.raise_for_status()
            species_data = response.json()
            return {"habitat": species_data.get("habitat", {})}
        except requests.RequestException as e:
            raise PokemonServiceError(f"Error fetching habitat: {str(e)}")

    def get_pokemon_encounters(self, name: str) -> List:
        """Get encounter locations for a Pokemon"""
        try:
            response = requests.get(f"{self.base_url}/pokemon/{name.lower()}/encounters")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise PokemonServiceError(f"Error fetching encounters: {str(e)}")


class PokemonServiceError(Exception):
    """Custom exception for Pokemon service errors"""
    pass 