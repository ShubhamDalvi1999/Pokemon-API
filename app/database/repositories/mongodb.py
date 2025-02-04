from pymongo import MongoClient
from app.database.repositories.base import DatabaseRepository
from app.database.models.pokemon import PokemonDocument

class MongoDBRepository(DatabaseRepository):
    """MongoDB repository implementation"""
    
    CURRENT_SCHEMA_VERSION = 2  # Increment this when schema changes
    
    def __init__(self, connection_string: str, db_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db.pokemon
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        self.collection.create_index("name", unique=True)
        self.collection.create_index("schema_version")

    def save_pokemon(self, pokemon_data: dict):
        """Save Pokemon data to MongoDB"""
        pokemon = PokemonDocument(**pokemon_data)
        data = pokemon.to_dict()
        data['schema_version'] = self.CURRENT_SCHEMA_VERSION
        
        # Upsert with schema version
        result = self.collection.update_one(
            {"name": data["name"]},
            {"$set": data},
            upsert=True
        )
        return data

    def get_pokemon(self, name: str):
        """Retrieve Pokemon data from MongoDB"""
        doc = self.collection.find_one({"name": name})
        if doc:
            # Check if document needs migration
            if doc.get('schema_version', 1) < self.CURRENT_SCHEMA_VERSION:
                doc = self._migrate_document(doc)
        return doc

    def _migrate_document(self, doc):
        """Migrate document to current schema version"""
        current_version = doc.get('schema_version', 1)
        
        # Migration from version 1 to 2 (adding base_experience)
        if current_version < 2:
            doc['base_experience'] = None
            doc['schema_version'] = 2
            self.collection.update_one(
                {"_id": doc["_id"]},
                {"$set": doc}
            )
        
        return doc

    def get_all_pokemon(self):
        """Retrieve all Pokemon from MongoDB"""
        return list(self.collection.find())

    def delete_pokemon(self, name: str):
        """Delete Pokemon from MongoDB"""
        result = self.collection.delete_one({"name": name})
        return result.deleted_count > 0

    def update_pokemon(self, name: str, pokemon_data: dict):
        """Update Pokemon data in MongoDB"""
        result = self.collection.update_one(
            {"name": name},
            {"$set": pokemon_data}
        )
        if result.modified_count > 0:
            return self.get_pokemon(name)
        return None

    def health_check(self):
        """Check MongoDB connection health"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False 