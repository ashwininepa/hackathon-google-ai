import uvicorn
import yaml
import os
from google.cloud import bigquery
from google.cloud import aiplatform

def setup_environment():
    """Set up the GCP environment"""
    # Set project ID
    os.environ["GOOGLE_CLOUD_PROJECT"] = "hackathon-playground-461714"
    
    # Initialize BigQuery client and create dataset if it doesn't exist
    client = bigquery.Client()
    dataset_id = "footway_support"
    dataset_ref = client.dataset(dataset_id)
    
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
    
    # Initialize Vertex AI
    aiplatform.init(
        project="hackathon-playground-461714",
        location="us-central1"
    )

if __name__ == "__main__":
    # Load configuration
    with open("config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    # Setup environment
    setup_environment()
    
    # Run the API server
    uvicorn.run(
        "src.api.app:app",
        host=config['api']['host'],
        port=config['api']['port'],
        reload=True
    ) 