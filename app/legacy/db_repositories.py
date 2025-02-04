from abc import ABC, abstractmethod
from models import PokemonSQL, PokemonNoSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import pyodbc

class DatabaseRepository(ABC):
    @abstractmethod
    def save_pokemon(self, pokemon_data):
        pass

    @abstractmethod
    def get_pokemon(self, name):
        pass

class PostgresRepository(DatabaseRepository):
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_pokemon(self, pokemon_data):
        pokemon = PokemonSQL(**pokemon_data)
        self.session.add(pokemon)
        self.session.commit()
        return pokemon

    def get_pokemon(self, name):
        return self.session.query(PokemonSQL).filter_by(name=name).first()

class MongoDBRepository(DatabaseRepository):
    def __init__(self, connection_string, db_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db.pokemon

    def save_pokemon(self, pokemon_data):
        pokemon = PokemonNoSQL(**pokemon_data)
        return self.collection.insert_one(pokemon.to_dict())

    def get_pokemon(self, name):
        return self.collection.find_one({"name": name})

class BigQueryRepository(DatabaseRepository):
    def __init__(self, project_id, dataset_id):
        try:
            # Debug information
            print("Environment variables:")
            print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
            print(f"BIGQUERY_DATASET: {os.getenv('BIGQUERY_DATASET')}")
            print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
            
            creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not creds_path:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
            
            # Convert to absolute path if needed
            creds_path = os.path.abspath(creds_path)
            print(f"Absolute credentials path: {creds_path}")
            
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
            
            print(f"Loading credentials from: {creds_path}")
            credentials = service_account.Credentials.from_service_account_file(creds_path)
            
            print(f"Initializing BigQuery client with project: {project_id}")
            self.client = bigquery.Client(
                project=project_id,
                credentials=credentials
            )
            self.dataset_id = dataset_id
            self.table_id = "pokemon"
            print(f"Successfully connected to BigQuery project: {project_id}")
            self._ensure_table_exists()
        except Exception as e:
            print(f"Error initializing BigQuery: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            raise

    def _ensure_table_exists(self):
        """Ensure the Pokemon table exists in BigQuery"""
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            
            # Try to get dataset (don't create if doesn't exist)
            try:
                self.client.get_dataset(dataset_ref)
                print(f"Dataset {self.dataset_id} exists")
            except Exception as e:
                print(f"Dataset {self.dataset_id} does not exist. Please create it manually in the BigQuery console.")
                raise Exception(f"Dataset {self.dataset_id} not found. Error: {str(e)}")
            
            # Ensure table exists
            table_ref = dataset_ref.table(self.table_id)
            try:
                self.client.get_table(table_ref)
                print(f"Table {self.table_id} exists")
            except Exception:
                schema = [
                    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("types", "JSON"),
                    bigquery.SchemaField("abilities", "JSON"),
                    bigquery.SchemaField("moves", "JSON"),
                    bigquery.SchemaField("stats", "JSON"),
                    bigquery.SchemaField("height", "INTEGER"),
                    bigquery.SchemaField("weight", "INTEGER"),
                ]
                table = bigquery.Table(table_ref, schema=schema)
                self.client.create_table(table, exists_ok=True)
                print(f"Created table {self.table_id}")
        except Exception as e:
            print(f"Error ensuring table exists: {str(e)}")
            raise

    def save_pokemon(self, pokemon_data):
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
        table = self.client.get_table(table_ref)
        
        # Format data for BigQuery
        rows_to_insert = [{
            "name": pokemon_data["name"],
            "types": pokemon_data.get("types", []),
            "abilities": pokemon_data.get("abilities", []),
            "moves": pokemon_data.get("moves", []),
            "stats": pokemon_data.get("stats", []),
            "height": pokemon_data.get("height", 0),
            "weight": pokemon_data.get("weight", 0)
        }]
        
        errors = self.client.insert_rows_json(table, rows_to_insert)
        if errors:
            raise Exception(f"Error inserting rows: {errors}")
        return pokemon_data

    def get_pokemon(self, name):
        query = f"""
            SELECT * FROM `{self.dataset_id}.{self.table_id}`
            WHERE name = @name
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("name", "STRING", name)
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        rows = list(query_job.result())
        return rows[0] if rows else None

class RedshiftRepository(DatabaseRepository):
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_pokemon(self, pokemon_data):
        pokemon = PokemonSQL(**pokemon_data)
        self.session.add(pokemon)
        self.session.commit()
        return pokemon

    def get_pokemon(self, name):
        return self.session.query(PokemonSQL).filter_by(name=name).first()

class AzureSQLRepository(DatabaseRepository):
    def __init__(self, connection_string):
        self.conn = pyodbc.connect(connection_string)
        self.cursor = self.conn.cursor()

    def save_pokemon(self, pokemon_data):
        query = """
            INSERT INTO pokemon (name, types, abilities, moves, stats, height, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            pokemon_data["name"],
            str(pokemon_data["types"]),
            str(pokemon_data["abilities"]),
            str(pokemon_data["moves"]),
            str(pokemon_data["stats"]),
            pokemon_data["height"],
            pokemon_data["weight"]
        ))
        self.conn.commit()

    def get_pokemon(self, name):
        query = "SELECT * FROM pokemon WHERE name = ?"
        self.cursor.execute(query, [name])
        return self.cursor.fetchone() 