"""
test_api_auth.py

Unit tests for authentication API endpoints (login, password management, etc).
"""

import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.auth_user import AuthUser
from app.core.auth import get_password_hash, create_access_token
from tests.auth_test_utils import get_auth_headers, create_test_user

# Use the standard test client
client = TestClient(app)


def test_login_success(db_session: Session):
    """Test successful login with valid credentials."""
    # Create a test user
    username = "test_login_user"
    password = "Test123Password!"
    
    # Create user directly in the database
    test_user = AuthUser(
        username=username,
        password_hash=get_password_hash(password),
        email="test_login@example.com",
        role="admin",
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    
    # Perform login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify last_login was updated
    db_session.refresh(test_user)
    assert test_user.last_login is not None
    # The last_login should be within the last minute
    assert test_user.last_login > datetime.utcnow() - timedelta(minutes=1)


def test_login_invalid_credentials(db_session: Session):
    """Test login with invalid credentials."""
    # Create a test user
    username = "test_invalid_login"
    password = "Test123Password!"
    
    # Create user directly in the database
    test_user = AuthUser(
        username=username,
        password_hash=get_password_hash(password),
        email="test_invalid@example.com",
        role="admin",
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    
    # Attempt login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "WrongPassword123!"}
    )
    
    # Verify response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect username or password"
    
    # Attempt login with non-existent user
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent_user", "password": password}
    )
    
    # Verify response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect username or password"

def test_reset_password(db_session: Session, monkeypatch):
    """Test password reset endpoint."""
    # Create a test user with an email (needed for reset)
    username = "reset_password_user"
    password = "Test123Password!"
    email = "reset@example.com"
    
    # Create user directly in the database
    test_user = AuthUser(
        username=username,
        password_hash=get_password_hash(password),
        email=email,
        role="admin",
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    
    # Mock the send_code function to avoid actually sending emails
    send_code_calls = []
    def mock_send_code(db=None, payload=None):
        send_code_calls.append({
            "payload": payload
        })
        return {"status": "success", "message": "Code sent successfully"}
    
    # Apply the monkeypatch
    monkeypatch.setattr("app.api.auth.send_code", mock_send_code)
    
    # Request password reset
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"username": username}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "password reset" in data["message"].lower() or "account exists" in data["message"].lower()
    
    # Verify mock was called with correct data
    assert len(send_code_calls) == 1
    assert "payload" in send_code_calls[0]
    assert send_code_calls[0]["payload"]["contact"] == email
    assert send_code_calls[0]["payload"]["contact_type"] == "email"
    assert "code" in send_code_calls[0]["payload"]
    assert "custom_message" in send_code_calls[0]["payload"]
    
    # We need to import verify_password for this test
    from app.core.auth import verify_password
    
    # Check that the password was actually updated in the database
    db_session.refresh(test_user)
    # The old password should no longer work (but we can't test the new one since it's random)
    assert not verify_password(password, test_user.password_hash)

def test_change_password(db_session: Session):
    """Test changing password for an authenticated user."""
    # Create a test user
    username = "test_change_pwd_user"
    old_password = "OldPassword123!"
    new_password = "NewPassword456!"
    
    # Create user directly in the database
    test_user = AuthUser(
        username=username,
        password_hash=get_password_hash(old_password),
        email="change_pwd@example.com",
        role="admin",
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    
    # First login to get a valid token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": old_password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Change password with valid token and correct old password
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": old_password,
            "new_password": new_password
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "success" in data["message"].lower()
    
    # Verify password was changed in database
    db_session.refresh(test_user)
    # Import verify_password if not already imported
    from app.core.auth import verify_password
    
    # Old password should no longer work
    assert not verify_password(old_password, test_user.password_hash)
    # New password should work
    assert verify_password(new_password, test_user.password_hash)
    
    # Try logging in with new password
    new_login = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": new_password}
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()

def test_verify_code(db_session: Session, monkeypatch):
    """Test verification code validation endpoint."""
    # Setup test data
    import uuid
    code = "123456"
    contact_email = "verify@example.com"
    
    # Mock dependencies to isolate the test
    # We'll need to mock the crud operation that looks up the verification code
    from app.crud import verification_code as crud_verification_code
    from app.models.verification_code import VerificationCode
    from datetime import datetime, timedelta
    
    # Create mock Contact and VerificationCode objects
    from app.models.contact import Contact
    
    # Create a mock contact
    contact_id = "test-contact-id"
    test_contact = Contact(
        id=contact_id,
        encrypted_value="encrypted_email_value",
        contact_type="email"
    )
    
    # Create a mock verification code
    test_verification = VerificationCode(
        id=str(uuid.uuid4()),
        user_id=contact_id,  # This should match the contact ID
        code=code,
        sent_to=contact_email,
        purpose="opt-in",
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        status="pending"  # Using a string value
    )
    
    # Mock get_or_create_contact to return our test contact
    def mock_get_or_create_contact(db, contact_val, contact_type=None):
        if contact_val == contact_email:
            return test_contact, contact_email
        return None, None
    
    # Mock the database query for verification code
    class MockQueryFactory:
        def __init__(self, valid_code):
            self.valid_code = valid_code
            
        def __call__(self, model):
            if model == VerificationCode:
                return self.MockQuery(self.valid_code)
            # Fall back to the original for other models
            return db_session.query(model)
            
        class MockQuery:
            def __init__(self, valid_code):
                self.valid_code = valid_code
                self.filters = []
                
            def filter(self, *conditions):
                self.filters.extend(conditions)
                return self
                
            def first(self):
                # Check if we're querying for the wrong code
                for condition in self.filters:
                    # This is a simplified check to see if 'wrong-code' is part of the condition
                    if str(condition).find("wrong-code") > -1:
                        return None
                return test_verification
    
    # Apply the monkeypatches
    monkeypatch.setattr("app.api.preferences.get_or_create_contact", mock_get_or_create_contact)
    
    # Apply the query monkeypatch with our factory
    mock_query_factory = MockQueryFactory(valid_code=code)
    monkeypatch.setattr(db_session, "query", mock_query_factory)
    
    # Test valid verification
    response = client.post(
        "/api/v1/preferences/verify-code",
        json={
            "code": code,
            "contact": contact_email,
            "contact_type": "email"
        }
    )
    
    # Verify success response
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "ok" in data
    assert data["ok"] == True
    assert "contact" in data
    
    # For the invalid code test, we need to modify our mock to return None for the wrong code
    def mock_query_for_invalid_code(model):
        if model == VerificationCode:
            return MockInvalidQuery()
        # Fall back to the original for other models
        return db_session.query(model)
    
    class MockInvalidQuery:
        def filter(self, *args, **kwargs):
            return self
        
        def first(self):
            # Always return None to simulate invalid code
            return None
    
    # Override the query patch for the invalid test
    monkeypatch.setattr(db_session, "query", mock_query_for_invalid_code)
    
    # Test invalid code
    response = client.post(
        "/api/v1/preferences/verify-code",
        json={
            "code": "wrong-code",
            "contact": contact_email,
            "contact_type": "email"
        }
    )
    
    # Verify error response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid or expired verification code" in data["detail"]
