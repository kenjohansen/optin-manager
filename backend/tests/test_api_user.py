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
    payload = {"email": f"testuser_{unique}@example.com", "phone": f"+1234567{unique}"}
    response = client.post("/api/v1/contacts/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["phone"] == payload["phone"]
    assert "id" in data

def test_read_contact(db_session):
    # First, create a contact
    unique = str(uuid.uuid4())[:8]
    payload = {"email": f"readuser_{unique}@example.com", "phone": f"+1234567{unique}"}
    create_resp = client.post("/api/v1/contacts/", json=payload)
    contact_id = create_resp.json()["id"]
    # Now, get the contact
    response = client.get(f"/api/v1/contacts/{contact_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["phone"] == payload["phone"]
    assert data["id"] == contact_id

def test_update_contact(db_session):
    # Create contact
    unique = str(uuid.uuid4())[:8]
    payload = {"email": f"updateuser_{unique}@example.com", "phone": f"+1234567{unique}"}
    create_resp = client.post("/api/v1/contacts/", json=payload)
    contact_id = create_resp.json()["id"]
    # Update contact
    update_payload = {"email": f"updated_{unique}@example.com", "phone": f"+1234567{unique}", "status": "inactive"}
    response = client.put(f"/api/v1/contacts/{contact_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == update_payload["email"]
    assert data["status"] == "inactive"

def test_delete_contact(db_session):
    # Create contact
    unique = str(uuid.uuid4())[:8]
    payload = {"email": f"deleteuser_{unique}@example.com", "phone": f"+1234567{unique}"}
    create_resp = client.post("/api/v1/contacts/", json=payload)
    contact_id = create_resp.json()["id"]
    # Delete contact
    response = client.delete(f"/api/v1/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    # Confirm contact is gone
    get_resp = client.get(f"/api/v1/contacts/{contact_id}")
    assert get_resp.status_code == 404
