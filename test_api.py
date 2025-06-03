import requests
import json

def test_api():
    # Test cases
    test_cases = [
        {
            "message": "I received wrong shoes, I want to return them",
            "language": "en"
        },
        {
            "message": "Min beställning har inte kommit fram än, jag är väldigt arg!",
            "language": "sv"
        },
        {
            "message": "Ich habe die falsche Größe erhalten und möchte umtauschen",
            "language": "de"
        }
    ]
    
    # API endpoint
    url = "http://localhost:8080/predict"
    
    # Test each case
    for case in test_cases:
        print(f"\nTesting message: {case['message']}")
        response = requests.post(url, json=case)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Category: {result['category']}")
            print(f"Handled by: {result['handled_by']}")
            print(f"Anger level: {result['anger_level']}")
            print(f"Response: {result['response']}")
            print(f"Explanation: {result['explanation']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    test_api() 