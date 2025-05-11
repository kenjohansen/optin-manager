"""
test_api_contact_additional.py

Additional tests to improve coverage for the contact API module,
focusing on filtering, error conditions, and edge cases.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.models.contact import Contact, ContactTypeEnum
from app.models.consent import Consent, ConsentStatusEnum
import os
from datetime import datetime, timedelta
from jose import jwt
import uuid

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

def test_list_contacts_with_admin_auth():
    """Test listing contacts with admin authentication."""
    # Get admin headers for authentication
    headers = get_auth_headers(role="admin")
    
    # Simple query without filters
    response = client.get("/api/v1/contacts/", headers=headers)
    assert response.status_code == 200
    
    # Verify basic response format
    data = response.json()
    assert "contacts" in data 
    assert isinstance(data["contacts"], list)

def test_list_contacts_with_parameters():
    """Test the contact list endpoint accepts different parameters."""
    # Get admin headers for authentication
    headers = get_auth_headers(role="admin")
    
    # Test various parameter combinations
    params = [
        "?search=test",
        "?consent=opt_in",
        "?time_window=30",
        "?limit=10",
        "?skip=0&limit=5"
    ]
    
    for param in params:
        response = client.get(f"/api/v1/contacts/{param}", headers=headers)
        # Just verify the endpoint accepts these parameters without error
        assert response.status_code == 200
        # Basic response structure check
        data = response.json()
        assert "contacts" in data
        assert isinstance(data["contacts"], list)

def test_get_contact_not_found():
    """Test getting a contact that doesn't exist."""
    # Get admin headers for authentication
    headers = get_auth_headers(role="admin")
    
    # Use a random UUID that doesn't exist
    nonexistent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/contacts/{nonexistent_id}", headers=headers)
    
    # Should return 404 Not Found
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()
