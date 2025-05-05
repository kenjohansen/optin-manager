"""
Test script to verify authentication and file upload with correct credentials
"""
import os
import requests
import json
from PIL import Image, ImageDraw

# Constants
API_BASE = "http://127.0.0.1:8000/api/v1"
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")

# Create a test image
def create_test_image(filename="test_auth_logo.png"):
    img = Image.new('RGB', (200, 100), color='green')
    draw = ImageDraw.Draw(img)
    draw.text((50, 40), 'Auth Test Logo', fill='white')
    img.save(filename)
    print(f"Created test image: {filename}")
    return filename

# Login and get token
def login(username="admin", password="adminpass"):  # Correct password from auth.py
    url = f"{API_BASE}/auth/login"
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print(f"Got token: {token[:10]}...")
            return token
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

# Test customization endpoint with token
def test_customization_endpoint(token):
    url = f"{API_BASE}/customization"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"GET customization status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authentication works for GET /customization")
            return True
        else:
            print(f"❌ Authentication failed for GET /customization: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing customization endpoint: {e}")
        return False

# Upload logo with token
def upload_logo(token, image_path):
    url = f"{API_BASE}/customization"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'logo': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'primary': '#00ff00',
                'secondary': '#ff00ff',
                'company_name': 'Auth Test Company',
                'privacy_policy_url': 'https://example.com/privacy'
            }
            
            # Print exact request details
            print(f"POST URL: {url}")
            print(f"Authorization: Bearer {token[:10]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
            print(f"POST customization status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                logo_url = result.get("logo_url")
                if logo_url:
                    print(f"Logo URL: {logo_url}")
                    
                    # Check if the file exists in the uploads directory
                    filename = os.path.basename(logo_url.split('?')[0])
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    
                    if os.path.exists(filepath):
                        print(f"✅ Logo file exists at {filepath}")
                        print(f"File size: {os.path.getsize(filepath)} bytes")
                        return True
                    else:
                        print(f"❌ Logo file does not exist at {filepath}")
                        # List all files in the directory
                        print("Files in upload directory:")
                        for f in os.listdir(UPLOAD_DIR):
                            print(f"  - {f} ({os.path.getsize(os.path.join(UPLOAD_DIR, f))} bytes)")
                        return False
                else:
                    print("❌ No logo URL in response")
                    return False
            else:
                print(f"❌ Upload failed: {response.text}")
                return False
    except Exception as e:
        print(f"Error uploading logo: {e}")
        return False

# Main function
def main():
    # Create test image
    image_path = create_test_image()
    
    # Login and get token
    token = login()
    if not token:
        print("Login failed, cannot proceed with tests")
        return
    
    # Test authentication
    if not test_customization_endpoint(token):
        print("Authentication test failed, cannot proceed with upload test")
        return
    
    # Test upload
    if upload_logo(token, image_path):
        print("✅ Logo upload test passed")
    else:
        print("❌ Logo upload test failed")
    
    # Clean up
    os.remove(image_path)
    print(f"Removed test image: {image_path}")

if __name__ == "__main__":
    main()
