"""
Simple test script to verify file upload functionality.
This will create a test image and attempt to upload it to the backend.
"""

import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import json

# Create a test image
def create_test_image(filename="test_logo.png", size=(200, 100), color="blue", text="Test Logo"):
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    draw.text((size[0]//4, size[1]//3), text, fill="white")
    
    # Save to file
    img.save(filename)
    print(f"Created test image: {filename}")
    return filename

# Upload the image
def upload_image(filename, token=None):
    url = "http://127.0.0.1:8000/api/v1/customization"
    
    # Prepare headers
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Prepare form data
    with open(filename, 'rb') as f:
        files = {'logo': (os.path.basename(filename), f, 'image/png')}
        data = {
            'primary': '#1976d2',
            'secondary': '#9c27b0',
            'company_name': 'Test Company',
            'privacy_policy_url': 'https://example.com/privacy'
        }
        
        print(f"Uploading {filename} to {url}")
        response = requests.post(url, files=files, data=data, headers=headers)
        
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response

# Get login token
def get_token(username="admin", password="admin"):
    url = "http://127.0.0.1:8000/api/v1/auth/login"
    data = {"username": username, "password": password}
    
    response = requests.post(
        url, 
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Got token: {token[:10]}...")
        return token
    else:
        print(f"Failed to get token: {response.text}")
        return None

# Verify the uploaded file exists
def verify_file_exists(filename):
    filepath = os.path.join("static", "uploads", filename)
    if os.path.exists(filepath):
        print(f"✅ File exists at {filepath}")
        print(f"File size: {os.path.getsize(filepath)} bytes")
        return True
    else:
        print(f"❌ File does not exist at {filepath}")
        return False

# Main function
def main():
    # Create test image
    test_image = create_test_image()
    
    # Get token
    token = get_token()
    
    # Upload image
    response = upload_image(test_image, token)
    
    # Parse response
    if response.status_code == 200:
        data = response.json()
        logo_url = data.get("logo_url")
        print(f"Logo URL from response: {logo_url}")
        
        # Extract filename from URL
        if logo_url:
            filename = os.path.basename(logo_url)
            verify_file_exists(filename)
    
    # Clean up
    os.remove(test_image)
    print("Test completed")

if __name__ == "__main__":
    main()
