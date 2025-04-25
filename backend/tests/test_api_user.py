"""
test_api_user.py

Unit tests for User API endpoints in the OptIn Manager backend.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.user import Contact
from app.schemas.user import ContactCreate

client = TestClient(app)

def test_create_contact(db_session):
    unique = str(uuid.uuid4())[:8]
    # Use the new schema with contact_value and contact_type
    payload = {"contact_value": f"testuser_{unique}@example.com", "contact_type": "email"}
    response = client.post("/api/v1/contacts/", json=payload)
    assert response.status_code == 200, f"Failed to create contact: {response.text}"
    data = response.json()
    assert "masked_value" in data
    assert data["contact_type"] == payload["contact_type"]
    assert "id" in data

def test_read_contact(db_session):
    # First, create a contact
    unique = str(uuid.uuid4())[:8]
    payload = {"contact_value": f"readuser_{unique}@example.com", "contact_type": "email"}
    create_resp = client.post("/api/v1/contacts/", json=payload)
    assert create_resp.status_code == 200, f"Failed to create contact: {create_resp.text}"
    contact_id = create_resp.json()["id"]
    
    # Now, get the contact
    response = client.get(f"/api/v1/contacts/{contact_id}")
    assert response.status_code == 200, f"Failed to get contact: {response.text}"
    data = response.json()
    assert "masked_value" in data
    assert data["contact_type"] == payload["contact_type"]
    assert data["id"] == contact_id

def test_update_contact(db_session):
    # Create contact
    unique = str(uuid.uuid4())[:8]
    payload = {"contact_value": f"updateuser_{unique}@example.com", "contact_type": "email"}
    create_resp = client.post("/api/v1/contacts/", json=payload)
    assert create_resp.status_code == 200, f"Failed to create contact: {create_resp.text}"
    contact_id = create_resp.json()["id"]
    
    # Update contact - only update status since contact_value and contact_type are immutable
    update_payload = {"status": "inactive"}
    response = client.put(f"/api/v1/contacts/{contact_id}", json=update_payload)
    assert response.status_code == 200, f"Failed to update contact: {response.text}"
    data = response.json()
    assert "masked_value" in data
    assert data["contact_type"] == payload["contact_type"]
    assert data["status"] == "inactive"

def test_delete_contact(db_session):
    # Create contact
    unique = str(uuid.uuid4())[:8]
    payload = {"contact_value": f"deleteuser_{unique}@example.com", "contact_type": "email"}
    create_resp = client.post("/api/v1/contacts/", json=payload)
    assert create_resp.status_code == 200, f"Failed to create contact: {create_resp.text}"
    contact_id = create_resp.json()["id"]
    
    # Delete contact
    response = client.delete(f"/api/v1/contacts/{contact_id}")
    assert response.status_code == 200, f"Failed to delete contact: {response.text}"
    assert response.json()["ok"] is True
    
    # Confirm contact is gone
    get_resp = client.get(f"/api/v1/contacts/{contact_id}")
    assert get_resp.status_code == 404, "Contact should not exist after deletion"
