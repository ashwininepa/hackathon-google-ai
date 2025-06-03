# Footway Customer Support AI

This project implements an AI-powered customer support system for Footway using Google's Gemini model. The system can classify customer messages, analyze sentiment, and generate appropriate responses in multiple languages.

## Features

- Message classification using Gemini AI
- Sentiment analysis for customer messages
- Multi-language support
- Automatic routing to human agents when needed
- BigQuery integration for data storage
- RESTful API interface

## Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Access to Gemini API
- BigQuery access

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd footway-ai-support
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud authentication:
```bash
gcloud auth application-default login
gcloud config set project hackathon-playground-461714
```

4. Create necessary GCP resources:
```bash
# Enable required APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

## Running the Application

1. Start the API server:
```bash
python run.py
```

2. Test the API:
```bash
python test_api.py
```

## API Endpoints

### POST /predict
Process a customer message and generate a response.

Request body:
```json
{
    "message": "Customer message text",
    "language": "en"  // Optional, defaults to English
}
```

Response:
```json
{
    "response": "Generated response",
    "category": "Message category",
    "handled_by": "ai_agent or human_agent",
    "confidence": 0.95,
    "anger_level": 0.3,
    "explanation": "Classification explanation"
}
```

### GET /health
Health check endpoint.

## Project Structure

```
footway-ai-support/
├── config/
│   └── config.yaml
├── src/
│   ├── data/
│   │   └── bigquery_client.py
│   ├── models/
│   │   └── gemini_client.py
│   └── api/
│       └── app.py
├── requirements.txt
├── run.py
└── test_api.py
```

## Configuration

Edit `config/config.yaml` to modify:
- Project settings
- BigQuery configuration
- Gemini model parameters
- API settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.