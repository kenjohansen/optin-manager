"""
test_api_contact.py

Unit tests for Contact API endpoints in the OptIn Manager backend.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from tests.auth_test_utils import get_auth_headers
from tests.test_utils import remove_timestamp_fields

client = TestClient(app)

def test_create_contact(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create with email contact type
    payload = {
        "contact_value": "testcontact@example.com",
        "contact_type": "email"
    }
    response = client.post("/api/v1/contacts/", json=payload, headers=headers)
    assert response.status_code == 200, f"Failed to create contact: {response.text}"
    
    data = response.json()
    # Remove timestamp fields for comparison
    data = remove_timestamp_fields(data)
    
    # The ContactOut schema uses masked_value instead of contact_value
    assert data["contact_type"] == payload["contact_type"]
    assert "masked_value" in data
    assert "id" in data

def test_read_contact(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # First, create a contact
    payload = {
        "contact_value": "readcontact@example.com",
        "contact_type": "email"
    }
    create_resp = client.post("/api/v1/contacts/", json=payload, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create contact: {create_resp.text}"
    
    contact_id = create_resp.json()["id"]
    
    # Now, get the contact
    response = client.get(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200, f"Failed to get contact: {response.text}"
    
    data = remove_timestamp_fields(response.json())
    assert data["contact_type"] == payload["contact_type"]
    assert "masked_value" in data
    assert data["id"] == contact_id

def test_update_contact(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create contact
    payload = {
        "contact_value": "updatecontact@example.com",
        "contact_type": "email"
    }
    create_resp = client.post("/api/v1/contacts/", json=payload, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create contact: {create_resp.text}"
    
    contact_id = create_resp.json()["id"]
    
    # Update contact
    update_payload = {"status": "inactive"}
    response = client.put(f"/api/v1/contacts/{contact_id}", json=update_payload, headers=headers)
    assert response.status_code == 200, f"Failed to update contact: {response.text}"
    
    data = remove_timestamp_fields(response.json())
    assert data["status"] == update_payload["status"]
    assert "masked_value" in data

def test_delete_contact(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create contact
    payload = {
        "contact_value": "deletecontact@example.com",
        "contact_type": "email"
    }
    create_resp = client.post("/api/v1/contacts/", json=payload, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create contact: {create_resp.text}"
    
    contact_id = create_resp.json()["id"]
    
    # Delete contact
    response = client.delete(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200, f"Failed to delete contact: {response.text}"
    assert response.json()["ok"] is True
    
    # Verify deletion
    get_resp = client.get(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert get_resp.status_code == 404, "Contact should not exist after deletion"
