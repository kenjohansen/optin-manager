"""
Simple debugging script for file upload functionality.
This script will:
1. Generate a test image with a timestamp
2. Save it directly to the uploads folder
3. Upload it via the API
4. Compare the results
"""

import os
import sys
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Constants
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
API_URL = "http://127.0.0.1:8000/api/v1/customization"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
print(f"Upload directory: {UPLOAD_DIR}")
print(f"Directory exists: {os.path.exists(UPLOAD_DIR)}")
print(f"Directory is writable: {os.access(UPLOAD_DIR, os.W_OK)}")

# Create a test image with timestamp
def create_test_image(filename=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not filename:
        filename = f"test_logo_{timestamp}.png"
    
    # Create a new image with timestamp text
    img = Image.new('RGB', (400, 200), color='red')
    draw = ImageDraw.Draw(img)
    draw.text((50, 100), f"Test Logo {timestamp}", fill="white")
    
    # Save directly to the uploads folder
    direct_path = os.path.join(UPLOAD_DIR, f"direct_{filename}")
    img.save(direct_path)
    print(f"Directly saved image to: {direct_path}")
    print(f"File exists: {os.path.exists(direct_path)}")
    print(f"File size: {os.path.getsize(direct_path)} bytes")
    
    # Save a copy for API upload
    api_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"api_{filename}")
    img.save(api_path)
    print(f"Saved API upload image to: {api_path}")
    
    return direct_path, api_path, filename

# Get login token
def get_token():
    auth_url = "http://127.0.0.1:8000/api/v1/auth/login"
    try:
        response = requests.post(
            auth_url,
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"Got authentication token: {token[:10]}...")
            return token
        else:
            print(f"Failed to get token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

# Upload image via API
def upload_via_api(image_path, token):
    try:
        # Prepare the form data
        with open(image_path, 'rb') as f:
            files = {'logo': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'primary': '#ff0000',
                'secondary': '#00ff00',
                'company_name': 'Debug Company',
                'privacy_policy_url': 'https://example.com/privacy'
            }
            
            # Set headers with token
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            print(f"Uploading {image_path} to {API_URL}")
            print(f"Headers: {headers}")
            
            # Make the request
            response = requests.post(API_URL, files=files, data=data, headers=headers)
            
            print(f"Upload status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                logo_url = result.get("logo_url")
                print(f"Logo URL from response: {logo_url}")
                
                # Extract filename from URL
                if logo_url:
                    filename = os.path.basename(logo_url.split('?')[0])  # Remove query params
                    api_uploaded_path = os.path.join(UPLOAD_DIR, filename)
                    print(f"API should have saved to: {api_uploaded_path}")
                    
                    if os.path.exists(api_uploaded_path):
                        print(f"✅ API upload file exists at {api_uploaded_path}")
                        print(f"File size: {os.path.getsize(api_uploaded_path)} bytes")
                        return True, api_uploaded_path
                    else:
                        print(f"❌ API upload file does not exist at {api_uploaded_path}")
                        # List all files in the directory
                        print("Files in upload directory:")
                        for f in os.listdir(UPLOAD_DIR):
                            print(f"  - {f} ({os.path.getsize(os.path.join(UPLOAD_DIR, f))} bytes)")
                        return False, None
            
            return False, None
    except Exception as e:
        print(f"Error uploading via API: {e}")
        return False, None

# Check permissions and fix if needed
def fix_permissions():
    try:
        # Ensure the uploads directory has correct permissions
        os.chmod(UPLOAD_DIR, 0o755)
        print(f"Set permissions on {UPLOAD_DIR} to 755")
        
        # Check if we can write to the directory
        test_file = os.path.join(UPLOAD_DIR, "permission_test.txt")
        with open(test_file, 'w') as f:
            f.write("Permission test")
        
        if os.path.exists(test_file):
            print(f"✅ Successfully wrote test file to {test_file}")
            os.remove(test_file)
            print(f"Removed test file")
            return True
        else:
            print(f"❌ Failed to write test file to {test_file}")
            return False
    except Exception as e:
        print(f"Error fixing permissions: {e}")
        return False

# Main function
def main():
    # Fix permissions
    if not fix_permissions():
        print("Failed to fix permissions, exiting")
        return
    
    # Create test image
    direct_path, api_path, filename = create_test_image()
    
    # Get token
    token = get_token()
    if not token:
        print("Failed to get token, trying without authentication")
    
    # Upload via API
    success, api_uploaded_path = upload_via_api(api_path, token)
    
    # Compare the files
    if success:
        print("\nComparison:")
        print(f"Direct file: {direct_path} ({os.path.getsize(direct_path)} bytes)")
        print(f"API file: {api_uploaded_path} ({os.path.getsize(api_uploaded_path)} bytes)")
        
        # Check if they're different files
        if direct_path != api_uploaded_path:
            print("Files are in different locations as expected")
        else:
            print("WARNING: Files are in the same location, which is unexpected")
    
    # Clean up
    if os.path.exists(api_path):
        os.remove(api_path)
        print(f"Removed temporary file: {api_path}")
    
    print("\nDebug complete")

if __name__ == "__main__":
    main()
