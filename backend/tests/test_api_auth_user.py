"""
test_api_auth_user.py

Unit tests for authentication user (admin/staff/service account) API endpoints.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.deps import require_admin_user
from tests.auth_test_utils import get_auth_headers, create_test_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_admin_user():
    # Patch the dependency to always return a dummy admin user
    original_dependency = app.dependency_overrides.get(require_admin_user)
    app.dependency_overrides[require_admin_user] = lambda: type('User', (), {
        "id": str(uuid.uuid4()), 
        "username": "adminuser", 
        "role": "admin", 
        "is_active": True
    })()
    yield
    if original_dependency:
        app.dependency_overrides[require_admin_user] = original_dependency
    else:
        app.dependency_overrides.pop(require_admin_user, None)

# Test user data
ADMIN_USER = {"username": f"adminuser-{uuid.uuid4().hex[:8]}", "password": "AdminPass123!", "role": "admin"}
STAFF_USER = {"username": f"staffuser-{uuid.uuid4().hex[:8]}", "password": "StaffPass123!", "role": "support"}


def test_create_auth_user(db_session: Session):
    # Use auth headers to authenticate as admin
    headers = get_auth_headers(role="admin")
    
    # Create a unique test user
    test_user = {
        "username": f"testuser-{uuid.uuid4().hex[:8]}",
        "password": "TestPass123!",
        "role": "support"
    }
    
    response = client.post("/api/v1/auth_users/", json=test_user, headers=headers)
    assert response.status_code == 200, f"Failed to create user: {response.text}"
    
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["role"] == test_user["role"]
    assert data["is_active"] is True
    assert "id" in data


def test_get_auth_user(db_session: Session):
    # Use auth headers to authenticate as admin
    headers = get_auth_headers(role="admin")
    
    # Create a unique test user
    test_user = {
        "username": f"getuser-{uuid.uuid4().hex[:8]}",
        "password": "GetPass123!",
        "role": "support"
    }
    
    # Create user
    response = client.post("/api/v1/auth_users/", json=test_user, headers=headers)
    assert response.status_code == 200, f"Failed to create user: {response.text}"
    user_id = response.json()["id"]
    
    # Retrieve user by id
    get_resp = client.get(f"/api/v1/auth_users/{user_id}", headers=headers)
    assert get_resp.status_code == 200, f"Failed to get user: {get_resp.text}"
    
    data = get_resp.json()
    assert data["username"] == test_user["username"]
    assert data["role"] == test_user["role"]
    assert data["is_active"] is True
    assert data["id"] == user_id


def test_update_auth_user(db_session: Session):
    # Use auth headers to authenticate as admin
    headers = get_auth_headers(role="admin")
    
    # Create a unique test user
    test_user = {
        "username": f"updateuser-{uuid.uuid4().hex[:8]}",
        "password": "UpdatePass123!",
        "role": "support"
    }
    
    # Create user
    create_resp = client.post("/api/v1/auth_users/", json=test_user, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create user: {create_resp.text}"
    user_id = create_resp.json()["id"]
    
    # Update user
    update_payload = {"role": "admin", "is_active": False}
    resp = client.put(f"/api/v1/auth_users/{user_id}", json=update_payload, headers=headers)
    assert resp.status_code == 200, f"Failed to update user: {resp.text}"
    
    data = resp.json()
    assert data["role"] == "admin"
    assert data["is_active"] is False


def test_delete_auth_user(db_session: Session):
    # Use auth headers to authenticate as admin
    headers = get_auth_headers(role="admin")
    
    # Create a unique test user
    test_user = {
        "username": f"deleteuser-{uuid.uuid4().hex[:8]}",
        "password": "DeletePass123!",
        "role": "support"
    }
    
    # Create user
    create_resp = client.post("/api/v1/auth_users/", json=test_user, headers=headers)
    assert create_resp.status_code == 200, f"Failed to create user: {create_resp.text}"
    user_id = create_resp.json()["id"]
    
    # Delete user
    del_resp = client.delete(f"/api/v1/auth_users/{user_id}", headers=headers)
    assert del_resp.status_code == 200, f"Failed to delete user: {del_resp.text}"
    assert del_resp.json()["ok"] is True
    
    # Verify user is deleted
    get_resp = client.get(f"/api/v1/auth_users/{user_id}", headers=headers)
    assert get_resp.status_code == 404, "User should not exist after deletion"
