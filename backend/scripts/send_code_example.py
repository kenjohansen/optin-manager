import requests
import json

# Define the API endpoint
url = "http://127.0.0.1:8000/api/v1/preferences/send-code"

# Define the payload
payload = {
    "contact": "test@example.com",
    "purpose": "self_service",
    "preferences_url": "http://localhost:5173/preferences?contact=test@example.com"
}

# Send the request
response = requests.post(url, json=payload)

# Print the response
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
