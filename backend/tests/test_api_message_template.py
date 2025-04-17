"""
test_api_message_template.py

Unit tests for MessageTemplate CRUD API endpoints in the OptIn Manager backend.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.schemas.message_template import MessageTemplateCreate

client = TestClient(app)

def test_create_message_template(db_session):
    payload = {
        "name": f"WelcomeTemplate_{uuid.uuid4().hex[:8]}",
        "content": "Welcome, {{name}}!",
        "channel": "sms",
        "description": "A welcome message template."
    }
    response = client.post("/api/v1/message-templates/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["content"] == payload["content"]
    assert "id" in data

def test_read_message_template(db_session):
    payload = {
        "name": f"ReadTemplate_{uuid.uuid4().hex[:8]}",
        "content": "Read test template!",
        "channel": "sms",
        "description": "Read test."
    }
    create_resp = client.post("/api/v1/message-templates/", json=payload)
    template_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/message-templates/{template_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == template_id
    assert data["name"] == payload["name"]

def test_update_message_template(db_session):
    payload = {
        "name": f"UpdateTemplate_{uuid.uuid4().hex[:8]}",
        "content": "Update test template!",
        "channel": "sms",
        "description": "Update test."
    }
    create_resp = client.post("/api/v1/message-templates/", json=payload)
    template_id = create_resp.json()["id"]
    update_payload = {
        "name": payload["name"],
        "content": "Updated content!",
        "channel": "sms",
        "description": "Updated description."
    }
    response = client.put(f"/api/v1/message-templates/{template_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated content!"
    assert data["description"] == "Updated description."

def test_delete_message_template(db_session):
    payload = {
        "name": f"DeleteTemplate_{uuid.uuid4().hex[:8]}",
        "content": "Delete test template!",
        "channel": "sms",
        "description": "Delete test."
    }
    create_resp = client.post("/api/v1/message-templates/", json=payload)
    template_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/message-templates/{template_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    # Confirm template is gone
    get_resp = client.get(f"/api/v1/message-templates/{template_id}")
    assert get_resp.status_code == 404
