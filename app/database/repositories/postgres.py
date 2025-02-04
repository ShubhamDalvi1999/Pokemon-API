from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.repositories.base import DatabaseRepository
from app.database.models.pokemon import PokemonSQL

class PostgresRepository(DatabaseRepository):
    """PostgreSQL repository implementation"""
    
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_pokemon(self, pokemon_data: dict):
        """Save Pokemon data to PostgreSQL"""
        pokemon = PokemonSQL(**pokemon_data)
        self.session.add(pokemon)
        self.session.commit()
        return pokemon

    def get_pokemon(self, name: str):
        """Retrieve Pokemon data from PostgreSQL"""
        return self.session.query(PokemonSQL).filter_by(name=name).first()

    def get_all_pokemon(self):
        """Retrieve all Pokemon from PostgreSQL"""
        return self.session.query(PokemonSQL).all()

    def delete_pokemon(self, name: str):
        """Delete Pokemon from PostgreSQL"""
        pokemon = self.session.query(PokemonSQL).filter_by(name=name).first()
        if pokemon:
            self.session.delete(pokemon)
            self.session.commit()
            return True
        return False

    def update_pokemon(self, name: str, pokemon_data: dict):
        """Update Pokemon data in PostgreSQL"""
        pokemon = self.session.query(PokemonSQL).filter_by(name=name).first()
        if pokemon:
            for key, value in pokemon_data.items():
                setattr(pokemon, key, value)
            self.session.commit()
            return pokemon
        return None

    def health_check(self):
        """Check PostgreSQL connection health"""
        try:
            self.session.execute("SELECT 1")
            return True
        except Exception:
            return False 