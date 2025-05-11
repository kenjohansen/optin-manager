"""
tests/test_api_preferences_coverage.py

Tests specifically designed to improve code coverage of the preferences API
without making assumptions about validation behavior.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import uuid
from datetime import datetime, timedelta
from tests.auth_test_utils import get_auth_headers
from app.models.consent import Consent, ConsentStatusEnum, ConsentChannelEnum
from app.models.optin import OptIn, OptInStatusEnum
from app.core.encryption import generate_deterministic_id
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
import os

client = TestClient(app)

# Mock the code sending functionality for all tests in this file
@pytest.fixture(autouse=True)
def mock_send_code():
    """Mock the code sending functionality for tests."""
    with patch("app.utils.send_code.CodeSender.send_sms_code", return_value=True), \
         patch("app.utils.send_code.CodeSender.send_email_code", return_value=True):
        yield

# --- 1. Additional Send Code Coverage Tests ---

def test_send_code_with_email():
    """Test sending a verification code to an email address."""
    headers = get_auth_headers(role="admin")
    
    payload = {
        "contact": "test@example.com",
        "contact_type": "email",
        "purpose": "opt-in"
    }
    
    response = client.post("/api/v1/preferences/send-code", json=payload, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "ok" in data
    assert data["ok"] is True
    assert "dev_code" in data

# --- 2. Additional Get Preferences Coverage Tests ---

def test_get_preferences_admin_access():
    """Test that an admin can access preferences for any user."""
    headers = get_auth_headers(role="admin")
    
    # Create contact ID based on the contact value
    contact = "coverage_test@example.com"
    
    # Create a test contact and consent record in the database
    db = SessionLocal()
    try:
        from app.core.encryption import encrypt_pii
        contact_id = generate_deterministic_id(contact)
        
        # Add a contact if it doesn't exist
        existing_contact = db.query(Consent).filter_by(user_id=contact_id).first()
        if not existing_contact:
            # Add a test product if it doesn't exist
            product = db.query(OptIn).filter(OptIn.id == "coverage_test_product").first()
            if not product:
                product = OptIn(
                    id="coverage_test_product",
                    name="Coverage Test Product",
                    description="Test product for preferences coverage",
                    status=OptInStatusEnum.active
                )
                db.add(product)
                db.commit()
                
            # Create a consent record for the test contact
            consent = Consent(
                user_id=contact_id,
                optin_id="coverage_test_product",
                channel=ConsentChannelEnum.email,
                status=ConsentStatusEnum.opt_in
            )
            db.add(consent)
            db.commit()
    finally:
        db.close()
    
    # Get preferences for the contact
    response = client.get(f"/api/v1/preferences/user-preferences?contact={contact}", headers=headers)
    assert response.status_code == 200
    
    # Check that we get the contact and consent info
    data = response.json()
    assert "contact" in data
    assert "id" in data["contact"]
    assert data["contact"]["id"] == contact_id
    assert "programs" in data
    assert isinstance(data["programs"], list)

# --- 3. Database Helpers for Test Setup ---

@pytest.fixture
def setup_test_user_and_products():
    """Set up test user and products in the database."""
    # Create a test phone number
    contact = "+17775551234"
    contact_id = generate_deterministic_id(contact)
    
    # Set up the database with test products
    db = SessionLocal()
    try:
        # Add test products if they don't exist
        for product_id in ["test_prod1", "test_prod2"]:
            product = db.query(OptIn).filter(OptIn.id == product_id).first()
            if not product:
                product = OptIn(
                    id=product_id,
                    name=f"Test Product {product_id}",
                    description="Test product for preferences",
                    status=OptInStatusEnum.active
                )
                db.add(product)
        
        # Commit products
        db.commit()
        
        # Add consent records for the test products - one for email, one for SMS
        # First product with email consent
        consent1 = Consent(
            user_id=contact_id,
            optin_id="test_prod1",
            channel=ConsentChannelEnum.email,
            status=ConsentStatusEnum.opt_in
        )
        db.add(consent1)
        
        # Second product with SMS consent
        consent2 = Consent(
            user_id=contact_id,
            optin_id="test_prod2",
            channel=ConsentChannelEnum.sms,
            status=ConsentStatusEnum.opt_out
        )
        db.add(consent2)
        
        # Commit consents
        db.commit()
    finally:
        db.close()
    
    return contact

# --- 4. Test Multiple Consent Records ---

def test_get_preferences_with_multiple_products(setup_test_user_and_products):
    """Test getting preferences for a user with multiple consent records."""
    headers = get_auth_headers(role="admin")
    contact = setup_test_user_and_products
    
    # Get preferences for the contact
    response = client.get(f"/api/v1/preferences/user-preferences?contact={contact}", headers=headers)
    assert response.status_code == 200
    
    # Check that we get both products
    data = response.json()
    assert "programs" in data
    assert len(data["programs"]) >= 2
    
    # Check that all consents are included for both products
    product_ids = [p.get("id") for p in data["programs"]]
    assert "test_prod1" in product_ids
    assert "test_prod2" in product_ids

# --- 5. Direct Bulk Preference Updates ---

def test_bulk_preference_update():
    """Test updating multiple preferences at once."""
    # Get an admin token for sending codes
    headers = get_auth_headers(role="admin")
    
    # First, send a verification code
    contact = "+17775559876"
    send_payload = {
        "contact": contact,
        "contact_type": "phone",
        "purpose": "opt-in"
    }
    
    send_response = client.post("/api/v1/preferences/send-code", json=send_payload, headers=headers)
    assert send_response.status_code == 200
    
    # Get the code from the response 
    code = send_response.json()["dev_code"]
    
    # Verify the code to get a token
    verify_payload = {
        "code": code,
        "contact": contact,
        "contact_type": "phone"
    }
    
    verify_response = client.post("/api/v1/preferences/verify-code", json=verify_payload)
    assert verify_response.status_code == 200
    token = verify_response.json()["token"]
    
    # Set up the database with test products
    db = SessionLocal()
    try:
        for product_id in ["bulk_prod1", "bulk_prod2", "bulk_prod3"]:
            product = db.query(OptIn).filter(OptIn.id == product_id).first()
            if not product:
                product = OptIn(
                    id=product_id,
                    name=f"Bulk Product {product_id}",
                    description="Test bulk update product",
                    status=OptInStatusEnum.active
                )
                db.add(product)
        db.commit()
    finally:
        db.close()
    
    # Use the token to update multiple preferences
    update_headers = {"Authorization": f"Bearer {token}"}
    update_payload = {
        "preferences": {
            "bulk_prod1": {
                "email": True,
                "sms": False
            },
            "bulk_prod2": {
                "email": False,
                "sms": True
            },
            "bulk_prod3": {
                "email": True,
                "sms": True
            }
        }
    }
    
    update_response = client.patch("/api/v1/preferences/user-preferences", json=update_payload, headers=update_headers)
    assert update_response.status_code == 200
    
    # Verify response 
    data = update_response.json()
    assert "success" in data
    assert data["success"] is True
