from sqlalchemy import Column, Integer, String, Boolean, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

class PokemonNoSQL:
    """NoSQL document structure for Pokemon data"""
    def __init__(self, name, types, abilities, moves, stats, height, weight):
        self.name = name
        self.types = types
        self.abilities = abilities
        self.moves = moves
        self.stats = stats
        self.height = height
        self.weight = weight

    def to_dict(self):
        return {
            "name": self.name,
            "types": self.types,
            "abilities": self.abilities,
            "moves": self.moves,
            "stats": self.stats,
            "height": self.height,
            "weight": self.weight
        } 