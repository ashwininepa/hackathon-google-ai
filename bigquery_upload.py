import sys
import os
import uuid

from google.cloud import bigquery
from datetime import datetime
from src.bot import CustomerSupportBot


# Add the project root to Python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))



def upload_bot_responses_to_bigquery():
    """
    Upload customer support bot responses to BigQuery.
    Uses test queries from the bot and uploads the responses to the specified table.
    """
    # Initialize the BigQuery client
    client = bigquery.Client()
    
    # Define dataset and table
    dataset_id = "synthetic_customer_conversations"
    table_id = "customer_support_translated_sentiment"
    table_ref = f"{client.project}.{dataset_id}.{table_id}"
    
    # Initialize the bot
    bot = CustomerSupportBot()
    print("Bot initialized successfully!")
    
    # Test queries (same as in the main function)
    test_queries = [
        "I want to cancel my subscription",
        "I need a refund for my last purchase", 
        "The app is not working properly",
        "Where is my package?",
        "How do I reset my password?"
    ]
    
    # Process each query and prepare data for BigQuery
    rows_to_insert = []
    
    for query in test_queries:
        print(f"\nProcessing query: {query}")
        result = bot.get_response(query)
        
        # Map confidence to sentiment score (0.0-1.0)
        sentiment_score = 0.8 if result['confidence'] == "high" else 0.4
        
        # Create a row for BigQuery
        row = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "original_language": "en",  # Assuming English as default
            "category": result['category'],
            "incoming_email_original": query,
            "reply_original": result['response'],
            "incoming_email_en": query,  # Same as original since it's already in English
            "reply_en": result['response'],
            "new_broad_category": result['category'],
            "incoming_email_cleaned": query,  # In a real system, you might clean the text
            "sentiment_score": sentiment_score,
            "sentiment_magnitude": sentiment_score * 0.8,  # Example calculation
            "assigned_to": "ai_bot",
            "emotion_tag": "neutral"  # You could refine this with sentiment analysis
        }
        
        rows_to_insert.append(row)
        print(f"Prepared row for: {query}")
    
    # Insert rows into BigQuery
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    
    if errors:
        print(f"Error inserting rows: {errors}")
    else:
        print(f"Successfully inserted {len(rows_to_insert)} rows into {table_ref}")

if __name__ == "__main__":
    upload_bot_responses_to_bigquery()