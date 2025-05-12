"""
tests/test_api_preferences.py

Unit tests for the Preferences API endpoints in the OptIn Manager backend.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import uuid
from datetime import datetime, timedelta
from tests.auth_test_utils import get_auth_headers
from tests.test_utils import remove_timestamp_fields
from app.models.consent import Consent, ConsentStatusEnum, ConsentChannelEnum
from app.models.optin import OptIn, OptInStatusEnum
from app.core.encryption import generate_deterministic_id
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

client = TestClient(app)

# Mock the send_verification_code function in the preferences API
@pytest.fixture(autouse=True)
def mock_send_code():
    """Mock the code sending functionality for tests."""
    # Patch both the SMS and email send methods to return success
    with patch("app.utils.send_code.CodeSender.send_sms_code", return_value=True), \
         patch("app.utils.send_code.CodeSender.send_email_code", return_value=True):
        yield

@pytest.mark.skip(reason="SMS provider Twilio not yet implemented")
def test_send_verification_code():
    """Test sending a verification code to a contact."""
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create a test payload
    payload = {
        "contact": "+12345678901",
        "contact_type": "phone",
        "purpose": "opt-in"
    }
    
    # Send the verification code
    response = client.post("/api/v1/preferences/send-code", json=payload, headers=headers)
    assert response.status_code == 200, f"Failed to send verification code: {response.text}"
    
    # Check the response
    data = response.json()
    assert "ok" in data
    assert data["ok"] is True
    assert "dev_code" in data  # Code is included for testing purposes in dev mode

@pytest.mark.skip(reason="SMS provider Twilio not yet implemented")
def test_verify_code():
    """Test verifying a code that was sent to a contact."""
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # First, send a verification code
    send_payload = {
        "contact": "+12345678902",
        "contact_type": "phone",
        "purpose": "opt-in"
    }
    
    send_response = client.post("/api/v1/preferences/send-code", json=send_payload, headers=headers)
    assert send_response.status_code == 200, f"Failed to send verification code: {send_response.text}"
    
    # Get the code from the response
    code = send_response.json()["dev_code"]
    
    # Create a verification payload
    verify_payload = {
        "contact": "+12345678902",
        "contact_type": "phone",
        "code": code
    }
    
    # Verify the code
    verify_response = client.post("/api/v1/preferences/verify-code", json=verify_payload, headers=headers)
    assert verify_response.status_code == 200, f"Failed to verify code: {verify_response.text}"
    
    # Check the response
    data = verify_response.json()
    assert "ok" in data
    assert data["ok"] is True
    assert "token" in data
    assert data["token"] is not None

@pytest.mark.skip(reason="SMS provider Twilio not yet implemented")
def test_get_preferences_with_token():
    """Test getting preferences using a token."""
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # First, send a verification code
    send_payload = {
        "contact": "+12345678903",
        "contact_type": "phone",
        "purpose": "opt-in"
    }
    
    send_response = client.post("/api/v1/preferences/send-code", json=send_payload, headers=headers)
    assert send_response.status_code == 200, f"Failed to send verification code: {send_response.text}"
    
    # Get the code from the response
    code = send_response.json()["dev_code"]
    
    # Verify the code to get a token
    verify_payload = {
        "contact": "+12345678903",
        "contact_type": "phone",
        "code": code
    }
    
    verify_response = client.post("/api/v1/preferences/verify-code", json=verify_payload, headers=headers)
    assert verify_response.status_code == 200, f"Failed to verify code: {verify_response.text}"
    
    # Get the token from the response
    token = verify_response.json()["token"]
    
    # Create headers with the token
    token_headers = {"Authorization": f"Bearer {token}"}
    
    # Get the preferences
    get_response = client.get("/api/v1/preferences/user-preferences", headers=token_headers)
    assert get_response.status_code == 200, f"Failed to get preferences: {get_response.text}"
    
    # Check the response
    data = get_response.json()
    assert "contact" in data
    assert "programs" in data
    assert isinstance(data["programs"], list)

@pytest.mark.skip(reason="SMS provider Twilio not yet implemented")
def test_get_preferences_with_contact_param():
    """Test getting preferences using a contact parameter."""
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # First, send a verification code
    send_payload = {
        "contact": "+12345678904",
        "contact_type": "phone",
        "purpose": "opt-in"
    }
    
    send_response = client.post("/api/v1/preferences/send-code", json=send_payload, headers=headers)
    assert send_response.status_code == 200, f"Failed to send verification code: {send_response.text}"
    
    # Get the code from the response
    code = send_response.json()["dev_code"]
    
    # Verify the code to get a token
    verify_payload = {
        "contact": "+12345678904",
        "contact_type": "phone",
        "code": code
    }
    
    verify_response = client.post("/api/v1/preferences/verify-code", json=verify_payload, headers=headers)
    assert verify_response.status_code == 200, f"Failed to verify code: {verify_response.text}"
    
    # Get the preferences using the contact parameter
    get_response = client.get("/api/v1/preferences/user-preferences?contact=%2B12345678904")
    assert get_response.status_code == 200, f"Failed to get preferences: {get_response.text}"
    
    # Check the response
    data = get_response.json()
    assert "contact" in data
    assert "programs" in data
    assert isinstance(data["programs"], list)

@pytest.mark.skip(reason="SMS provider Twilio not yet implemented")
def test_update_preferences():
    """Test updating preferences for a contact."""
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # First, send a verification code
    send_payload = {
        "contact": "+12345678905",
        "contact_type": "phone",
        "purpose": "opt-in"
    }
    
    send_response = client.post("/api/v1/preferences/send-code", json=send_payload, headers=headers)
    assert send_response.status_code == 200, f"Failed to send verification code: {send_response.text}"
    
    # Get the code from the response
    code = send_response.json()["dev_code"]
    
    # Verify the code to get a token
    verify_payload = {
        "contact": "+12345678905",
        "contact_type": "phone",
        "code": code
    }
    
    verify_response = client.post("/api/v1/preferences/verify-code", json=verify_payload, headers=headers)
    assert verify_response.status_code == 200, f"Failed to verify code: {verify_response.text}"
    
    # Get the token from the response
    token = verify_response.json()["token"]
    
    # Create headers with the token
    token_headers = {"Authorization": f"Bearer {token}"}
    
    # Get the preferences to see what optins are available
    get_response = client.get("/api/v1/preferences/user-preferences", headers=token_headers)
    assert get_response.status_code == 200, f"Failed to get preferences: {get_response.text}"
    
    # Create an update payload with the new PATCH structure
    update_payload = {
        "programs": [
            {
                "id": "test-optin-id",  # This would normally be a real optin_id
                "opted_in": True
            }
        ]
    }

    # Update the preferences using PATCH
    update_response = client.patch("/api/v1/preferences/user-preferences", json=update_payload, headers=token_headers)
    assert update_response.status_code in (200, 204), f"Failed to patch preferences: {update_response.text}"

    # Test global opt-out
    global_opt_out_payload = {
        "programs": [],
        "global_opt_out": True,
        "comment": "Test global opt out"
    }
    global_opt_out_response = client.patch("/api/v1/preferences/user-preferences", json=global_opt_out_payload, headers=token_headers)
    assert global_opt_out_response.status_code in (200, 204), f"Failed to patch global opt-out: {global_opt_out_response.text}"
    
    # This might fail if there are no real optins available, but we're testing the API structure
    # In a real test, we would first create optins and then use their IDs
    
    # Check that the API endpoint exists and returns a response
    assert update_response.status_code in [200, 400, 404], f"Unexpected status code: {update_response.status_code}"
