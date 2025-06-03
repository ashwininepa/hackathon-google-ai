import google.generativeai as genai
import yaml
from typing import Dict, Any, List
import json

class GeminiClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Configure Gemini
        genai.configure(project=self.config['project']['project_id'])
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.config['gemini']['model_name'],
            generation_config={
                'temperature': self.config['gemini']['temperature'],
                'max_output_tokens': self.config['gemini']['max_output_tokens'],
                'top_p': self.config['gemini']['top_p'],
                'top_k': self.config['gemini']['top_k']
            }
        )
        
        # Load categories
        self.categories = self.config['model']['categories']
        
    def classify_message(self, message: str) -> Dict[str, Any]:
        """Classify customer message using Gemini"""
        prompt = f"""
        Analyze the following customer support message and classify it into one of these categories: {', '.join(self.categories)}.
        Also determine if the customer is angry (sentiment analysis) and provide a confidence score.
        
        Message: {message}
        
        Provide the response in JSON format with the following structure:
        {{
            "category": "category_name",
            "confidence": 0.95,
            "anger_level": 0.3,
            "explanation": "brief explanation of the classification"
        }}
        """
        
        response = self.model.generate_content(prompt)
        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # Fallback in case of invalid JSON
            return {
                "category": "UNKNOWN",
                "confidence": 0.0,
                "anger_level": 0.5,
                "explanation": "Failed to parse model response"
            }
    
    def generate_response(self, 
                         category: str, 
                         message: str, 
                         language: str,
                         anger_level: float) -> str:
        """Generate appropriate response using Gemini"""
        
        # Determine if human intervention is needed
        needs_human = (
            category in self.config['model']['human_intervention_categories'] or
            anger_level > self.config['model']['sentiment_threshold']
        )
        
        if needs_human:
            prompt = f"""
            The customer message indicates they need human assistance. 
            Generate a polite response in {language} that explains we're connecting them to a human agent.
            Message: {message}
            """
        else:
            prompt = f"""
            Generate a helpful customer support response in {language} for the following message.
            The message is categorized as {category}.
            The customer's anger level is {anger_level} (0-1 scale).
            
            Message: {message}
            
            Guidelines:
            1. Be empathetic and professional
            2. Provide clear next steps
            3. Include relevant information about returns, shipping, or other processes as needed
            4. Keep the response concise but complete
            """
        
        response = self.model.generate_content(prompt)
        return response.text 