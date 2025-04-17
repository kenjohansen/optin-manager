"""
test_api_consent.py

Unit tests for Consent API endpoints in the OptIn Manager backend.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.user import Contact
from app.schemas.consent import ConsentCreate

client = TestClient(app)

def create_user_for_consent():
    unique = str(uuid.uuid4())[:8]
    user_payload = {
        "email": f"consentuser_{unique}@example.com",
        "phone": f"+1234567{unique[:4]}"
    }
    user_resp = client.post("/api/v1/contacts/", json=user_payload)
    return user_resp.json()["id"]

def test_create_consent(db_session):
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "campaign_id": None,
        "channel": "sms",
        "status": "pending"
    }
    response = client.post("/api/v1/consents/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["channel"] == "sms"
    assert data["status"] == "pending"
    assert "id" in data

def test_read_consent(db_session):
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "campaign_id": None,
        "channel": "sms",
        "status": "pending"
    }
    create_resp = client.post("/api/v1/consents/", json=payload)
    consent_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/consents/{consent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == consent_id
    assert data["user_id"] == user_id

def test_update_consent(db_session):
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "campaign_id": None,
        "channel": "sms",
        "status": "pending"
    }
    create_resp = client.post("/api/v1/consents/", json=payload)
    consent_id = create_resp.json()["id"]
    update_payload = {"user_id": user_id, "campaign_id": None, "channel": "sms", "status": "opt_in"}
    response = client.put(f"/api/v1/consents/{consent_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "opt_in"

def test_delete_consent(db_session):
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "campaign_id": None,
        "channel": "sms",
        "status": "pending"
    }
    create_resp = client.post("/api/v1/consents/", json=payload)
    consent_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/consents/{consent_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    # Confirm consent is gone
    get_resp = client.get(f"/api/v1/consents/{consent_id}")
    assert get_resp.status_code == 404
