from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PokemonSQL(Base):
    """SQLAlchemy model for Pokemon data"""
    __tablename__ = 'pokemon'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    types = Column(JSON)
    abilities = Column(JSON)
    moves = Column(JSON)
    stats = Column(JSON)
    height = Column(Integer)
    weight = Column(Integer)
    sprites = Column(JSON)
    base_experience = Column(Integer, nullable=True)

class PokemonDocument:
    """Document model for NoSQL databases"""
    def __init__(self, name, types, abilities, moves, stats, height, weight, sprites, base_experience=None):
        self.name = name
        self.types = types
        self.abilities = abilities
        self.moves = moves
        self.stats = stats
        self.height = height
        self.weight = weight
        self.sprites = sprites
        self.base_experience = base_experience

    def to_dict(self):
        """Convert to dictionary for NoSQL storage"""
        return {
            "name": self.name,
            "types": self.types,
            "abilities": self.abilities,
            "moves": self.moves,
            "stats": self.stats,
            "height": self.height,
            "weight": self.weight,
            "sprites": self.sprites,
            "base_experience": self.base_experience
        } 