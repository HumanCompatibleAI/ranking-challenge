import time
from pprint import pprint

import requests

import sample_data

# This is a simple script that sends a POST request to the API and prints the response.
# Your server should be running on localhost:5001

# Wait for the Flask app to start up
time.sleep(2)

# Send POST request to the API
response = requests.post("http://localhost:5001/rank", json=sample_data.CHATGPT_EXAMPLE)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    try:
        # Attempt to parse the JSON response
        json_response = response.json()
        pprint(json_response)
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON response. Response may be empty.")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)
