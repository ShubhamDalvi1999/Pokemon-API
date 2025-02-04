import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
    GRAPHQL_URL = "https://beta.pokeapi.co/graphql/v1beta"
    
    # Database configurations (all optional)
    POSTGRES_URL = os.getenv('POSTGRES_URL', None)
    MONGODB_URL = os.getenv('MONGODB_URL', None)
    MONGODB_DB = os.getenv('MONGODB_DB', None)
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', None)
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', None)
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)

    @property
    def has_postgres(self):
        """Check if PostgreSQL is configured"""
        return bool(self.POSTGRES_URL)

    @property
    def has_mongodb(self):
        """Check if MongoDB is configured"""
        return bool(self.MONGODB_URL and self.MONGODB_DB)

    @property
    def has_bigquery(self):
        """Check if BigQuery is configured"""
        return bool(self.GOOGLE_CLOUD_PROJECT and 
                   self.BIGQUERY_DATASET and 
                   self.GOOGLE_APPLICATION_CREDENTIALS)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'default')
    return config[env]() 