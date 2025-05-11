"""
tests/test_api_provider_secrets.py

Unit tests for the provider secrets API endpoints.

These tests verify the functionality of the provider secrets API, which manages
the credentials for email and SMS providers used in the system.
"""

import pytest
import json
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.deps import require_admin_user, require_support_user
from app.models.customization import Customization
from app.api.provider_secrets import vault


client = TestClient(app)


@pytest.fixture(autouse=True)
def override_admin_user():
    # Use string ID for SQLite compatibility
    admin_user = type('User', (), {"id": "admin-user-id", "username": "admin", "role": "admin", "is_active": True})()
    app.dependency_overrides[require_admin_user] = lambda: admin_user
    app.dependency_overrides[require_support_user] = lambda: admin_user
    yield
    app.dependency_overrides.pop(require_admin_user, None)
    app.dependency_overrides.pop(require_support_user, None)


@pytest.fixture(scope="function")
def clean_provider_secrets():
    """Reset provider secrets for test isolation"""
    # Import locally to avoid import cycles
    from app.core.provider_vault import ProviderSecretsVault
    vault = ProviderSecretsVault()
    
    # Store existing keys to restore afterward
    keys_to_check = [
        "EMAIL_ACCESS_KEY", "EMAIL_SECRET_KEY", "EMAIL_REGION", "EMAIL_FROM_ADDRESS",
        "SMS_ACCESS_KEY", "SMS_SECRET_KEY", "SMS_REGION"
    ]
    
    # Save original values
    original_values = {}
    for key in keys_to_check:
        original_values[key] = vault.get_secret(key)
        
    # Clear all secrets for test
    for key in keys_to_check:
        vault.delete_secret(key)
        
    yield
    
    # Restore original values
    for key, value in original_values.items():
        if value:
            vault.set_secret(key, value)


def test_set_provider_secret_email(clean_provider_secrets):
    """Test setting email provider credentials"""
    payload = {
        "provider_type": "email",
        "access_key": "test-access-key",
        "secret_key": "test-secret-key",
        "region": "us-west-2",
        "from_address": "test@example.com"
    }
    
    response = client.post("/api/v1/provider-secrets/set", json=payload)
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    
    # Verify the secrets were stored by checking status endpoint
    status_response = client.get("/api/v1/provider-secrets/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["email_configured"] is True


def test_set_provider_secret_sms(clean_provider_secrets):
    """Test setting SMS provider credentials"""
    payload = {
        "provider_type": "sms",
        "access_key": "test-sms-access-key",
        "secret_key": "test-sms-secret-key",
        "region": "us-east-1"
    }
    
    response = client.post("/api/v1/provider-secrets/set", json=payload)
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    
    # Verify the secrets were stored by checking status endpoint
    status_response = client.get("/api/v1/provider-secrets/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["sms_configured"] is True


def test_set_provider_secret_invalid_type(clean_provider_secrets):
    """Test setting provider credentials with invalid provider type"""
    payload = {
        "provider_type": "invalid",
        "access_key": "test-access-key",
        "secret_key": "test-secret-key"
    }
    
    response = client.post("/api/v1/provider-secrets/set", json=payload)
    assert response.status_code == 400
    assert "Invalid provider_type" in response.text


def test_get_secrets_status(db_session: Session):
    """Test getting provider secrets status"""
    # Make sure we have a customization record
    db_customization = db_session.query(Customization).first()
    if not db_customization:
        db_customization = Customization()
        db_session.add(db_customization)
    
    # Set specific status values for testing
    db_customization.email_connection_status = "test-status-email"
    db_customization.sms_connection_status = "test-status-sms"
    db_session.commit()
    
    response = client.get("/api/v1/provider-secrets/status")
    assert response.status_code == 200
    
    data = response.json()
    # We're testing that the status values from database are returned correctly
    # We don't test email_configured/sms_configured since they depend on the vault state
    assert data["email_status"] == "test-status-email"
    assert data["sms_status"] == "test-status-sms"


def test_delete_provider_secret(clean_provider_secrets, db_session: Session):
    """Test deleting provider credentials"""
    # First set up the credentials
    email_payload = {
        "provider_type": "email",
        "access_key": "test-access-key",
        "secret_key": "test-secret-key"
    }
    
    client.post("/api/v1/provider-secrets/set", json=email_payload)
    
    # Make sure we have a customization record
    db_customization = db_session.query(Customization).first()
    if not db_customization:
        db_customization = Customization()
        db_session.add(db_customization)
    
    # Set status values for testing
    db_customization.email_connection_status = "connected"
    db_session.commit()
    
    # Verify credentials are set
    status_resp = client.get("/api/v1/provider-secrets/status")
    assert status_resp.json()["email_configured"] is True
    
    # Now delete the credentials
    delete_payload = {
        "provider_type": "email"
    }
    
    response = client.post("/api/v1/provider-secrets/delete", json=delete_payload)
    assert response.status_code == 200
    
    # Verify credentials are deleted
    status_resp = client.get("/api/v1/provider-secrets/status")
    assert status_resp.json()["email_configured"] is False
    
    # Check that the connection status was reset
    db_session.refresh(db_customization)
    assert db_customization.email_connection_status == "untested"


@patch.dict(os.environ, {"ENV": "dev"})
def test_provider_connection_dev_mode(clean_provider_secrets, db_session: Session):
    """Test provider connection in dev mode (mocked response)"""
    # Set up credentials first
    email_payload = {
        "provider_type": "email",
        "access_key": "test-access-key",
        "secret_key": "test-secret-key"
    }
    client.post("/api/v1/provider-secrets/set", json=email_payload)
    
    # Make sure we have a customization record with untested status
    db_customization = db_session.query(Customization).first()
    if not db_customization:
        db_customization = Customization()
        db_session.add(db_customization)
    
    db_customization.email_connection_status = "untested"
    db_session.commit()
    
    # Test the connection
    test_payload = {
        "provider_type": "email"
    }
    
    response = client.post("/api/v1/provider-secrets/test", json=test_payload)
    assert response.status_code == 200
    
    # In dev mode, we should get a success response without actually connecting
    assert response.json()["ok"] is True
    assert "mocked" in response.json()["message"]
    
    # The status should be updated to "tested"
    db_session.refresh(db_customization)
    assert db_customization.email_connection_status == "tested"


def test_provider_connection_no_credentials(clean_provider_secrets, db_session: Session):
    """Test provider connection when credentials are not configured"""
    # First ensure no credentials are set
    for key in ["EMAIL_ACCESS_KEY", "EMAIL_SECRET_KEY", "EMAIL_REGION"]:
        vault.delete_secret(key)
    
    # Make sure we have a customization record
    db_customization = db_session.query(Customization).first()
    if not db_customization:
        db_customization = Customization()
        db_session.add(db_customization)
    
    db_session.commit()
    
    # Test the connection
    test_payload = {
        "provider_type": "email"
    }
    
    response = client.post("/api/v1/provider-secrets/test", json=test_payload)
    assert response.status_code == 400
    
    # Response should indicate credentials not configured
    assert "Credentials not configured" in response.text


def test_provider_connection_invalid_type(clean_provider_secrets, db_session: Session):
    """Test provider connection with invalid provider type"""
    # Test the connection with an invalid provider type
    test_payload = {
        "provider_type": "invalid"
    }
    
    response = client.post("/api/v1/provider-secrets/test", json=test_payload)
    assert response.status_code == 400
    
    # Response should indicate invalid provider type
    assert "Invalid provider_type" in response.text


@patch.dict(os.environ, {"ENV": "production"})
@patch("boto3.client")
def test_provider_connection_email_aws_ses(mock_boto3_client, clean_provider_secrets, db_session: Session):
    """Test email provider connection with AWS SES in production mode"""
    # Mock the AWS SES client
    mock_ses = MagicMock()
    mock_boto3_client.return_value = mock_ses
    
    # Set up email credentials
    email_payload = {
        "provider_type": "email",
        "access_key": "test-access-key",
        "secret_key": "test-secret-key",
        "region": "us-west-2",
        "from_address": "test@example.com"
    }
    client.post("/api/v1/provider-secrets/set", json=email_payload)
    
    # Make sure we have a customization record
    db_customization = db_session.query(Customization).first()
    if not db_customization:
        db_customization = Customization()
        db_session.add(db_customization)
    
    db_customization.email_connection_status = "untested"
    db_session.commit()
    
    # Test the connection
    test_payload = {
        "provider_type": "email"
    }
    
    # Configure mock to simulate successful connection
    mock_ses.get_account_sending_enabled.return_value = {"Enabled": True}
    
    response = client.post("/api/v1/provider-secrets/test", json=test_payload)
    assert response.status_code == 200
    
    # Verify the mock was called correctly
    mock_boto3_client.assert_called_once_with(
        'ses',
        region_name='us-west-2',
        aws_access_key_id='test-access-key',
        aws_secret_access_key='test-secret-key'
    )
    
    # The status should be updated
    db_session.refresh(db_customization)
    # In our test environment, the status is set to 'tested'
    assert db_customization.email_connection_status == "tested"
