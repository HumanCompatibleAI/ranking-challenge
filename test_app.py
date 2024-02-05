import requests
import time

# Sample data containing multiple text items
data = [
    {"text": "I love this product! It's amazing."},
    {"text": "This movie was terrible. I wouldn't recommend it."},
    {"text": "The food at that restaurant was average."},
]

# Wait for the Flask app to start up
time.sleep(2)

# Send POST request to the API
response = requests.post("http://localhost:5000/analyze_sentiment", json=data)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    try:
        # Attempt to parse the JSON response
        json_response = response.json()
        print(json_response)
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON response. Response may be empty.")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)