from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import yaml
from src.models.gemini_client import GeminiClient
from src.data.bigquery_client import BigQueryClient
import uuid
from datetime import datetime

app = FastAPI(title="Footway Customer Support AI")

# Load configuration
with open("config/config.yaml", 'r') as file:
    config = yaml.safe_load(file)

# Initialize clients
gemini_client = GeminiClient()
bigquery_client = BigQueryClient()

class CustomerMessage(BaseModel):
    message: str
    language: str = "en"  # Default to English

class Response(BaseModel):
    response: str
    category: str
    handled_by: str
    confidence: float
    anger_level: float
    explanation: str

@app.post("/predict", response_model=Response)
async def predict(message: CustomerMessage) -> Dict[str, Any]:
    try:
        # Generate unique message ID
        message_id = str(uuid.uuid4())
        
        # Get classification and sentiment
        classification = gemini_client.classify_message(message.message)
        
        # Generate response
        response = gemini_client.generate_response(
            category=classification['category'],
            message=message.message,
            language=message.language,
            anger_level=classification['anger_level']
        )
        
        # Determine if handled by human or AI
        handled_by = "human_agent" if (
            classification['category'] in config['model']['human_intervention_categories'] or
            classification['anger_level'] > config['model']['sentiment_threshold']
        ) else "ai_agent"
        
        # Store in BigQuery
        bigquery_client.insert_customer_message({
            "message_id": message_id,
            "customer_message": message.message,
            "timestamp": datetime.utcnow(),
            "language": message.language,
            "category": classification['category'],
            "sentiment_score": classification['anger_level'],
            "handled_by": handled_by,
            "response": response
        })
        
        return Response(
            response=response,
            category=classification['category'],
            handled_by=handled_by,
            confidence=classification['confidence'],
            anger_level=classification['anger_level'],
            explanation=classification['explanation']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 