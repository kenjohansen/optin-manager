import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
import pytest
from tests.auth_test_utils import get_auth_headers
from tests.test_utils import remove_timestamp_fields

client = TestClient(app)

def sample_verification_code_payload():
    return {
        "user_id": str(uuid.uuid4()),
        "code": "123456",
        "channel": "sms",
        "sent_to": "+1234567890",
        # Format the datetime as a string with timezone info
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "purpose": "opt-in",
        "status": "pending"
    }

def test_create_verification_code():
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    payload = sample_verification_code_payload()
    response = client.post("/api/v1/verification-codes/", json=payload, headers=headers)
    assert response.status_code == 200, f"Failed to create verification code: {response.text}"
    
    # Remove timestamp fields for comparison
    data = remove_timestamp_fields(response.json())
    
    assert data["user_id"] == payload["user_id"]
    assert data["code"] == payload["code"]
    assert data["channel"] == payload["channel"]
    assert data["sent_to"] == payload["sent_to"]
    assert data["purpose"] == payload["purpose"]
    assert data["status"] == payload["status"]
    assert "id" in data
    
    # Store the ID for other tests
    global verification_code_id
    verification_code_id = data["id"]

def test_read_verification_code():
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    payload = sample_verification_code_payload()
    create_resp = client.post("/api/v1/verification-codes/", json=payload, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create verification code: {create_resp.text}"
    
    code = create_resp.json()
    response = client.get(f"/api/v1/verification-codes/{code['id']}", headers=headers)
    assert response.status_code == 200, f"Failed to get verification code: {response.text}"
    
    # Remove timestamp fields for comparison
    data = remove_timestamp_fields(response.json())
    code = remove_timestamp_fields(code)
    
    assert data["id"] == code["id"]
    assert data["user_id"] == code["user_id"]
    assert data["code"] == code["code"]
    assert data["channel"] == code["channel"]
    assert data["sent_to"] == code["sent_to"]
    assert data["purpose"] == code["purpose"]
    assert data["status"] == code["status"]

def test_update_verification_code():
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create a verification code
    payload = sample_verification_code_payload()
    create_resp = client.post("/api/v1/verification-codes/", json=payload, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create verification code: {create_resp.text}"
    
    code = create_resp.json()
    
    # Update the verification code - only send the fields we want to update
    update_payload = {
        "status": "verified"  # Change status to verified
    }
    
    response = client.put(f"/api/v1/verification-codes/{code['id']}", json=update_payload, headers=headers)
    assert response.status_code == 200, f"Failed to update verification code: {response.text}"
    
    # Remove timestamp fields for comparison
    data = remove_timestamp_fields(response.json())
    code = remove_timestamp_fields(code)
    
    # Check that the status was updated
    assert data["status"] == "verified"
    
    # Check that other fields remain the same
    assert data["id"] == code["id"]
    assert data["user_id"] == code["user_id"]
    assert data["code"] == code["code"]
    assert data["channel"] == code["channel"]
    assert data["sent_to"] == code["sent_to"]
    assert data["purpose"] == code["purpose"]

def test_delete_verification_code():
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create a verification code
    payload = sample_verification_code_payload()
    create_resp = client.post("/api/v1/verification-codes/", json=payload, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create verification code: {create_resp.text}"
    
    code = create_resp.json()
    
    # Delete the verification code
    response = client.delete(f"/api/v1/verification-codes/{code['id']}", headers=headers)
    assert response.status_code == 200, f"Failed to delete verification code: {response.text}"
    
    # Verify it's gone
    get_resp = client.get(f"/api/v1/verification-codes/{code['id']}", headers=headers)
    assert get_resp.status_code == 404, "Verification code should not exist after deletion"
