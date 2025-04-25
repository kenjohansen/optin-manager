"""
test_api_message_crud.py

Unit tests for Message CRUD API endpoints in the OptIn Manager backend.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.user import Contact
from app.schemas.message import MessageCreate

client = TestClient(app)

def create_user_for_message():
    unique = str(uuid.uuid4())[:8]
    # Using the new Contact schema with contact_value and contact_type
    user_payload = {
        "contact_value": f"msguser_{unique}@example.com",
        "contact_type": "email"
    }
    user_resp = client.post("/api/v1/contacts/", json=user_payload)
    return user_resp.json()["id"]

def test_create_message(db_session):
    user_id = create_user_for_message()
    # Create a test optin ID as a string
    test_optin_id = str(uuid.uuid4())
    payload = {
        "user_id": user_id,
        "optin_id": test_optin_id,
        "channel": "sms",
        "content": "Hello!",
        "status": "pending"
    }
    # Add auth headers
    headers = {"Authorization": "Bearer test-token"}
    response = client.post("/api/v1/messages/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["content"] == "Hello!"
    assert data["status"] == "pending"
    assert "id" in data

def test_read_message(db_session):
    user_id = create_user_for_message()
    # Create a test optin ID as a string
    test_optin_id = str(uuid.uuid4())
    payload = {
        "user_id": user_id,
        "optin_id": test_optin_id,
        "channel": "sms",
        "content": "Read test!",
        "status": "pending"
    }
    # Add auth headers
    headers = {"Authorization": "Bearer test-token"}
    create_resp = client.post("/api/v1/messages/", json=payload, headers=headers)
    message_id = create_resp.json()["id"]
    
    response = client.get(f"/api/v1/messages/{message_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message_id
    assert data["user_id"] == user_id

def test_update_message(db_session):
    user_id = create_user_for_message()
    # Create a test optin ID as a string
    test_optin_id = str(uuid.uuid4())
    payload = {
        "user_id": user_id,
        "optin_id": test_optin_id,
        "channel": "sms",
        "content": "Update test!",
        "status": "pending"
    }
    # Add auth headers
    headers = {"Authorization": "Bearer test-token"}
    create_resp = client.post("/api/v1/messages/", json=payload, headers=headers)
    message_id = create_resp.json()["id"]
    update_payload = {"user_id": user_id, "optin_id": test_optin_id, "channel": "sms", "content": "Updated!", "status": "sent"}
    response = client.put(f"/api/v1/messages/{message_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated!"
    assert data["status"] == "sent"

def test_delete_message(db_session):
    user_id = create_user_for_message()
    # Create a test optin ID as a string
    test_optin_id = str(uuid.uuid4())
    payload = {
        "user_id": user_id,
        "optin_id": test_optin_id,
        "channel": "sms",
        "content": "Delete test!",
        "status": "pending"
    }
    # Add auth headers
    headers = {"Authorization": "Bearer test-token"}
    create_resp = client.post("/api/v1/messages/", json=payload, headers=headers)
    message_id = create_resp.json()["id"]
    
    response = client.delete(f"/api/v1/messages/{message_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True
    # Confirm message is gone
    get_resp = client.get(f"/api/v1/messages/{message_id}")
    assert get_resp.status_code == 404
