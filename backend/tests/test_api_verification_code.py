import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def sample_verification_code_payload():
    return {
        "user_id": str(uuid.uuid4()),
        "code": "123456",
        "channel": "sms",
        "sent_to": "+1234567890",
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
        "purpose": "opt-in",
        "status": "pending"
    }

def test_create_verification_code():
    payload = sample_verification_code_payload()
    response = client.post("/api/v1/verification-codes/", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["user_id"] == payload["user_id"]
    assert data["code"] == payload["code"]
    assert data["channel"] == payload["channel"]
    assert data["sent_to"] == payload["sent_to"]
    assert data["expires_at"].startswith(payload["expires_at"][:16])  # match up to minute
    assert data["purpose"] == payload["purpose"]
    assert data["status"] == payload["status"]
    assert "id" in data
    global verification_code_id
    verification_code_id = data["id"]

def test_read_verification_code():
    payload = sample_verification_code_payload()
    create_resp = client.post("/api/v1/verification-codes/", json=payload)
    assert create_resp.status_code == 200
    code = create_resp.json()
    response = client.get(f"/api/v1/verification-codes/{code['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == code["id"]
    assert data["user_id"] == code["user_id"]
    assert data["code"] == code["code"]
    assert data["channel"] == code["channel"]
    assert data["sent_to"] == code["sent_to"]
    assert data["expires_at"] == code["expires_at"]
    assert data["purpose"] == code["purpose"]
    assert data["status"] == code["status"]

def test_update_verification_code():
    payload = sample_verification_code_payload()
    create_resp = client.post("/api/v1/verification-codes/", json=payload)
    assert create_resp.status_code == 200
    code = create_resp.json()
    update_payload = {
        "user_id": code["user_id"],
        "code": "654321",
        "channel": "email",
        "sent_to": "user@example.com",
        "expires_at": code["expires_at"],
        "verified_at": datetime.utcnow().isoformat(),
        "purpose": "opt-out",
        "status": "verified"
    }
    response = client.put(f"/api/v1/verification-codes/{code['id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == code["id"]
    assert data["code"] == update_payload["code"]
    assert data["channel"] == update_payload["channel"]
    assert data["sent_to"] == update_payload["sent_to"]
    assert data["purpose"] == update_payload["purpose"]
    assert data["status"] == update_payload["status"]
    assert data["verified_at"].startswith(update_payload["verified_at"][:16])

def test_delete_verification_code():
    payload = sample_verification_code_payload()
    create_resp = client.post("/api/v1/verification-codes/", json=payload)
    assert create_resp.status_code == 200
    code = create_resp.json()
    response = client.delete(f"/api/v1/verification-codes/{code['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Confirm deletion
    get_resp = client.get(f"/api/v1/verification-codes/{code['id']}")
    assert get_resp.status_code == 404
