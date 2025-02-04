from google.cloud import bigquery
from google.oauth2 import service_account
import os
from app.database.repositories.base import DatabaseRepository
import logging

logger = logging.getLogger(__name__)

class BigQueryRepository(DatabaseRepository):
    """BigQuery repository implementation"""
    
    def __init__(self, project_id: str, dataset_id: str):
        try:
            creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not creds_path:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
            
            credentials = service_account.Credentials.from_service_account_file(creds_path)
            self.client = bigquery.Client(project=project_id, credentials=credentials)
            self.dataset_id = dataset_id
            self.table_id = "pokemon"
            self._ensure_table_exists()
        except Exception as e:
            raise Exception(f"Error initializing BigQuery: {str(e)}")

    def _ensure_table_exists(self):
        """Ensure the Pokemon table exists with the correct schema"""
        dataset_ref = self.client.dataset(self.dataset_id)
        table_ref = dataset_ref.table(self.table_id)
        
        try:
            self.client.get_table(table_ref)
        except Exception:
            # Table doesn't exist, create it
            schema = [
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("types", "JSON"),
                bigquery.SchemaField("abilities", "JSON"),
                bigquery.SchemaField("moves", "JSON"),
                bigquery.SchemaField("stats", "JSON"),
                bigquery.SchemaField("height", "INTEGER"),
                bigquery.SchemaField("weight", "INTEGER"),
                bigquery.SchemaField("sprites", "JSON"),
                bigquery.SchemaField("base_experience", "INTEGER")
            ]
            
            table = bigquery.Table(table_ref, schema=schema)
            self.client.create_table(table)

    def save_pokemon(self, pokemon_data: dict):
        """Save Pokemon data to BigQuery"""
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
            "weight": pokemon_data.get("weight", 0),
            "sprites": pokemon_data.get("sprites", {}),
            "base_experience": pokemon_data.get("base_experience")
        }]
        
        try:
            errors = self.client.insert_rows_json(table, rows_to_insert)
            if errors:
                raise Exception(f"Error inserting rows: {errors}")
            return pokemon_data
        except Exception as e:
            if "Streaming insert is not allowed in the free tier" in str(e):
                logger.warning("BigQuery streaming insert not available in free tier")
                return pokemon_data  # Return data without error to continue operation
            raise  # Re-raise other exceptions

    def get_pokemon(self, name: str):
        """Retrieve Pokemon data from BigQuery"""
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

    def get_all_pokemon(self):
        """Retrieve all Pokemon from BigQuery"""
        query = f"""
            SELECT * FROM `{self.dataset_id}.{self.table_id}`
        """
        query_job = self.client.query(query)
        return list(query_job.result())

    def delete_pokemon(self, name: str):
        """Delete Pokemon from BigQuery"""
        query = f"""
            DELETE FROM `{self.dataset_id}.{self.table_id}`
            WHERE name = @name
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("name", "STRING", name)
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        query_job.result()
        return True

    def update_pokemon(self, name: str, pokemon_data: dict):
        """Update Pokemon data in BigQuery"""
        # BigQuery doesn't support UPDATE, so we'll delete and insert
        self.delete_pokemon(name)
        pokemon_data["name"] = name
        return self.save_pokemon(pokemon_data)

    def health_check(self):
        """Check BigQuery connection health"""
        try:
            query = "SELECT 1"
            query_job = self.client.query(query)
            query_job.result()
            return True
        except Exception:
            return False 