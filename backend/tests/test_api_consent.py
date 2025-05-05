"""
test_api_consent.py

Unit tests for Consent API endpoints in the OptIn Manager backend.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.consent import ConsentCreate
from tests.auth_test_utils import get_auth_headers
from tests.test_utils import remove_timestamp_fields

client = TestClient(app)

def create_user_for_consent():
    unique = str(uuid.uuid4())[:8]
    # Create with email contact type
    user_payload = {
        "contact_value": f"consentuser_{unique}@example.com",
        "contact_type": "email"
    }
    # Get admin auth headers for creating contacts
    headers = get_auth_headers(role="admin")
    user_resp = client.post("/api/v1/contacts/", json=user_payload, headers=headers)
    assert user_resp.status_code == 200, f"Failed to create contact: {user_resp.text}"
    return user_resp.json()["id"]

def test_create_consent(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "optin_id": None,
        "channel": "sms",
        "status": "active",
        "source": "api"
    }
    
    # Create consent
    resp = client.post("/api/v1/consents/", json=payload, headers=headers)
    assert resp.status_code == 200, f"Failed to create consent: {resp.text}"
    
    consent = remove_timestamp_fields(resp.json())
    assert consent["user_id"] == user_id
    assert consent["status"] == "active"
    assert "id" in consent

def test_read_consent(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "optin_id": None,
        "channel": "sms",
        "status": "active",
        "source": "api"
    }
    
    # Create consent
    create_resp = client.post("/api/v1/consents/", json=payload, headers=headers)
    consent_id = create_resp.json()["id"]
    
    # Get consent
    get_resp = client.get(f"/api/v1/consents/{consent_id}", headers=headers)
    assert get_resp.status_code == 200, f"Failed to get consent: {get_resp.text}"
    data = remove_timestamp_fields(get_resp.json())
    assert data["id"] == consent_id
    assert data["user_id"] == user_id

def test_update_consent(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "optin_id": None,
        "channel": "sms",
        "status": "active",
        "source": "api"
    }
    
    # Create consent
    create_resp = client.post("/api/v1/consents/", json=payload, headers=headers)
    consent_id = create_resp.json()["id"]
    
    # Update consent
    update_payload = {"status": "opt_in"}
    response = client.put(f"/api/v1/consents/{consent_id}", json=update_payload, headers=headers)
    assert response.status_code == 200, f"Failed to update consent: {response.text}"
    data = remove_timestamp_fields(response.json())
    assert data["status"] == "opt_in"

def test_delete_consent(db_session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    user_id = create_user_for_consent()
    payload = {
        "user_id": user_id,
        "optin_id": None,
        "channel": "sms",
        "status": "active",
        "source": "api"
    }
    
    # Create consent
    create_resp = client.post("/api/v1/consents/", json=payload, headers=headers)
    consent_id = create_resp.json()["id"]
    
    # Delete consent
    delete_resp = client.delete(f"/api/v1/consents/{consent_id}", headers=headers)
    assert delete_resp.status_code == 200, f"Failed to delete consent: {delete_resp.text}"
    
    # Confirm deletion
    get_resp = client.get(f"/api/v1/consents/{consent_id}", headers=headers)
    assert get_resp.status_code == 404, "Consent should not exist after deletion"
