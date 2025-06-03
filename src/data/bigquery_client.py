from google.cloud import bigquery
from typing import List, Dict, Any
import yaml
import os

class BigQueryClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.client = bigquery.Client(project=self.config['project']['project_id'])
        self.dataset_id = self.config['bigquery']['dataset_id']
        
    def create_tables_if_not_exist(self):
        """Create necessary tables if they don't exist"""
        dataset_ref = self.client.dataset(self.dataset_id)
        
        # Customer Messages Table
        customer_messages_schema = [
            bigquery.SchemaField("message_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("customer_message", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("language", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("sentiment_score", "FLOAT"),
            bigquery.SchemaField("handled_by", "STRING"),
            bigquery.SchemaField("response", "STRING")
        ]
        
        table_id = f"{self.config['project']['project_id']}.{self.dataset_id}.{self.config['bigquery']['tables']['customer_messages']}"
        table = bigquery.Table(table_id, schema=customer_messages_schema)
        
        try:
            self.client.create_table(table, exists_ok=True)
        except Exception as e:
            print(f"Error creating table: {e}")
    
    def insert_customer_message(self, message_data: Dict[str, Any]):
        """Insert a new customer message into BigQuery"""
        table_id = f"{self.config['project']['project_id']}.{self.dataset_id}.{self.config['bigquery']['tables']['customer_messages']}"
        
        rows_to_insert = [message_data]
        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        
        if errors:
            raise Exception(f"Error inserting rows: {errors}")
    
    def get_training_data(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve training data from BigQuery"""
        query = f"""
        SELECT 
            customer_message,
            category,
            language
        FROM `{self.config['project']['project_id']}.{self.dataset_id}.{self.config['bigquery']['tables']['training_data']}`
        LIMIT {limit}
        """
        
        query_job = self.client.query(query)
        return [dict(row) for row in query_job] 