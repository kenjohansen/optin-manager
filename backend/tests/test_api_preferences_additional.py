"""
test_api_preferences_additional.py

Additional tests to improve coverage for the preferences API module,
focusing on previously uncovered code paths.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.verification_code import VerificationCode, VerificationStatusEnum
import os
from datetime import datetime, timedelta
from jose import jwt

# Create a test client
client = TestClient(app)

# Helper function to get authentication headers for testing
def get_auth_headers(role="user", user_id="test-user"):
    """Get authentication headers for the specified role."""
    secret_key = os.getenv("SECRET_KEY", "changeme")
    if role == "admin":
        payload = {
            "sub": "test-admin",
            "scope": "admin",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
    else:
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

def test_get_preferences_wrong_scope():
    """Test retrieving preferences with a token that has an invalid scope."""
    # Create a token with an invalid scope
    secret_key = os.getenv("SECRET_KEY", "changeme")
    payload = {
        "sub": "test-user",
        "scope": "invalid-scope",  # This scope doesn't exist
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get preferences with this token
    response = client.get("/api/v1/preferences/user-preferences", headers=headers)
    
    # The API accepts tokens with invalid scopes and defaults to regular user permissions
    assert response.status_code == 200
    # Check for the expected fields in the response
    assert "contact" in response.json()
    assert "programs" in response.json()

def test_request_with_expired_token():
    """Test making a request with an expired token."""
    # Create an expired token
    secret_key = os.getenv("SECRET_KEY", "changeme")
    payload = {
        "sub": "test-user",
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get preferences with this token
    response = client.get("/api/v1/preferences/user-preferences", headers=headers)
    
    # API returns 401 Unauthorized with a generic authentication required message
    assert response.status_code == 401
    assert "Authentication required" in response.text

def test_invalid_token_format():
    """Test making a request with an invalid token format."""
    # Use a malformed token
    headers = {"Authorization": "Bearer invalid_token_format"}
    
    # Try to get preferences with this token
    response = client.get("/api/v1/preferences/user-preferences", headers=headers)
    
    # API returns 401 Unauthorized with an authentication required message
    assert response.status_code == 401
    assert "Authentication required" in response.text

def test_bulk_update_with_product_ids():
    """Test the preference update with specific product IDs."""
    # First need to authenticate with a token
    # Get admin headers for code sending
    admin_headers = get_auth_headers(role="admin")
    
    # Send a verification code using email instead of phone to avoid SMS issues
    contact = "test@example.com"
    send_payload = {
        "contact": contact,
        "contact_type": "email",
        "purpose": "opt-in"
    }
    
    send_response = client.post("/api/v1/preferences/send-code", json=send_payload, headers=admin_headers)
    assert send_response.status_code == 200
    
    # Get the verification code
    code = send_response.json()["dev_code"]
    
    # Verify the code to get a token
    verify_payload = {
        "code": code,
        "contact": contact,
        "contact_type": "email"
    }
    
    verify_response = client.post("/api/v1/preferences/verify-code", json=verify_payload)
    assert verify_response.status_code == 200
    token = verify_response.json()["token"]
    
    # Now use the token to update preferences
    update_headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test payload with a list of product IDs
    # This tests a specific branch in the code that handles product_ids lists
    update_payload = {
        "preferences": {
            "product_ids": ["product1", "product2"],
            "email": True,
            "sms": False
        }
    }
    
    # Call the update endpoint with the token
    response = client.patch("/api/v1/preferences/user-preferences", json=update_payload, headers=update_headers)
    
    # Verify successful response
    assert response.status_code == 200
    assert "success" in response.json()
