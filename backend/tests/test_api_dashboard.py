"""
tests/test_api_dashboard.py

Unit tests for the dashboard API endpoints.

These tests verify that the dashboard statistics endpoint returns the
expected metrics and handles different time periods correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.models.auth_user import AuthUser
from app.models.optin import OptIn
from app.models.message import Message
from app.models.message_template import MessageTemplate
from app.models.contact import Contact
from app.models.consent import Consent
from app.core.deps import require_admin_user, require_support_user


client = TestClient(app)


@pytest.fixture(autouse=True)
def override_auth_user():
    """Override auth requirements for testing."""
    # Create mock admin user
    admin_user = type('User', (), {
        "id": "admin-user-id", 
        "username": "admin", 
        "role": "admin", 
        "is_active": True
    })()
    
    # Override the dependency
    app.dependency_overrides[require_admin_user] = lambda: admin_user
    app.dependency_overrides[require_support_user] = lambda: admin_user
    
    yield
    
    # Clean up
    app.dependency_overrides.pop(require_admin_user, None)
    app.dependency_overrides.pop(require_support_user, None)


def test_dashboard_stats_empty_db(db_session: Session):
    """Test dashboard stats with an empty database."""
    # Ensure database is empty
    db_session.query(AuthUser).delete()
    db_session.query(OptIn).delete()
    db_session.query(Message).delete()
    db_session.query(MessageTemplate).delete()
    db_session.query(Contact).delete()
    db_session.query(Consent).delete()
    db_session.commit()
    
    # Request dashboard stats
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    
    # Verify all counts are zero in empty database
    data = response.json()
    assert data["users"] == 0
    assert data["optins"]["total"] == 0  # optins is a dictionary with nested fields
    assert data["messages"]["total"] == 0
    assert data["templates"] == 0
    assert data["total_contacts"] == 0
    
    # Verify nested metrics
    assert data["consent"]["total"] == 0
    assert data["consent"]["active"] == 0
    assert data["verification"]["total"] == 0
    assert data["verification"]["successful"] == 0
    assert data["messages"]["status"]["delivered"] == 0
    assert isinstance(data["messages"]["volume_trend"], list)


def test_dashboard_stats_with_data(db_session: Session):
    """Test dashboard stats with some test data."""
    # Create test data
    
    # 1. Add a user
    user = AuthUser(
        username="testuser",
        email="test@example.com",
        password_hash="fake-hashed-password",
        role="admin",
        is_active=True
    )
    db_session.add(user)
    
    # 2. Add an opt-in program
    optin = OptIn(
        name="Test OptIn",
        description="Test OptIn Description",
        status="active"
    )
    db_session.add(optin)
    
    # 3. Add a message template
    template = MessageTemplate(
        name="Test Template",
        content="Hello {{name}}!",
        channel="email"
    )
    db_session.add(template)
    
    # 4. Add a contact
    contact = Contact(
        id="test-id-value",
        encrypted_value="contact@example.com",
        contact_type="email"
    )
    db_session.add(contact)
    
    # 5. Add consent
    consent = Consent(
        user_id=contact.id,
        optin_id=optin.id,
        channel="email",
        status="opt-in"
    )
    db_session.add(consent)
    
    # Commit to get proper IDs
    db_session.commit()
    
    # 6. Add a message
    message = Message(
        user_id=contact.id,
        optin_id=optin.id,
        template_id=template.id,
        content="Hello John!",
        status="delivered",
        channel="email"
    )
    db_session.add(message)
    
    db_session.commit()
    
    # Request dashboard stats
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    
    # Verify counts match the test data
    data = response.json()
    assert data["users"] == 1
    assert data["optins"]["total"] == 1
    assert data["messages"]["total"] == 1
    assert data["templates"] == 1
    assert data["total_contacts"] == 1
    
    # Verify nested metrics
    assert data["consent"]["total"] == 1
    assert data["consent"]["active"] == 1
    assert data["verification"]["total"] == 1
    assert data["verification"]["successful"] == 1
    assert data["messages"]["status"]["delivered"] == 1
    assert data["messages"]["status"]["failed"] == 0
    
    # Clean up
    db_session.query(Message).delete()
    db_session.query(Consent).delete()
    db_session.query(Contact).delete()
    db_session.query(MessageTemplate).delete()
    db_session.query(OptIn).delete()
    db_session.query(AuthUser).delete()
    db_session.commit()


def test_dashboard_stats_time_period(db_session: Session):
    """Test dashboard stats with different time periods."""
    # Create test data with different time periods
    now = datetime.utcnow()
    
    # 1. Add a user that logged in recently
    recent_user = AuthUser(
        username="recentuser",
        email="recent@example.com",
        password_hash="fake-hashed-password",
        role="admin",
        is_active=True
    )
    # Set created_at and last_login directly as we can't set them in constructor
    recent_user.created_at = now - timedelta(days=5)
    # Set last_login for recent user to be within the time period
    recent_user.last_login = now - timedelta(days=5)
    db_session.add(recent_user)
    
    # 2. Add a user that logged in long ago
    old_user = AuthUser(
        username="olduser",
        email="old@example.com",
        password_hash="fake-hashed-password",
        role="admin",
        is_active=True
    )
    # Set created_at and last_login directly
    old_user.created_at = now - timedelta(days=60)
    # Set last_login for old user to be outside the default time period (30 days)
    old_user.last_login = now - timedelta(days=60)
    db_session.add(old_user)
    
    # 3. Add a recent contact
    recent_contact = Contact(
        id="recent-id",
        encrypted_value="recent@example.com",
        contact_type="email"
    )
    # Set created_at directly
    recent_contact.created_at = now - timedelta(days=5)
    db_session.add(recent_contact)
    
    # 4. Add an old contact
    old_contact = Contact(
        id="old-id",
        encrypted_value="1234567890",
        contact_type="phone"
    )
    # Set created_at directly
    old_contact.created_at = now - timedelta(days=60)
    db_session.add(old_contact)
    
    db_session.commit()
    
    # Test with default time period (30 days)
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["system"]["users"]["active"] == 1  # Only recent user
    assert data["total_contacts"] == 2  # All contacts
    assert data["new_contacts"] == 1  # Only recent contact
    
    # Test with shorter time period (7 days)
    response = client.get("/api/v1/dashboard/stats?days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["users"] == 2  # All users
    assert data["system"]["users"]["active"] == 1  # Only recent user
    assert data["total_contacts"] == 2  # All contacts
    assert data["new_contacts"] == 1  # Only recent contact
    
    # Test with longer time period (90 days)
    response = client.get("/api/v1/dashboard/stats?days=90")
    assert response.status_code == 200
    data = response.json()
    assert data["users"] == 2  # All users
    assert data["system"]["users"]["active"] == 2  # All users active in last 90 days
    assert data["total_contacts"] == 2  # All contacts
    assert data["new_contacts"] == 2  # All contacts created in last 90 days
    
    # Clean up
    db_session.query(Contact).delete()
    db_session.query(AuthUser).delete()
    db_session.commit()
