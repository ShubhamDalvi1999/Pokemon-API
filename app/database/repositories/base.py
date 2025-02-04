from abc import ABC, abstractmethod

class DatabaseRepository(ABC):
    """Abstract base class for database repositories"""
    
    @abstractmethod
    def save_pokemon(self, pokemon_data: dict):
        """Save Pokemon data to database"""
        pass

    @abstractmethod
    def get_pokemon(self, name: str):
        """Retrieve Pokemon data from database"""
        pass

    @abstractmethod
    def get_all_pokemon(self):
        """Retrieve all Pokemon from database"""
        pass

    @abstractmethod
    def delete_pokemon(self, name: str):
        """Delete Pokemon from database"""
        pass

    @abstractmethod
    def update_pokemon(self, name: str, pokemon_data: dict):
        """Update Pokemon data in database"""
        pass

    @abstractmethod
    def health_check(self):
        """Check database connection health"""
        pass 