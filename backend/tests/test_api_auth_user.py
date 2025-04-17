"""
test_api_auth_user.py

Unit tests for authentication user (admin/staff/service account) API endpoints.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import types
from app.core.deps import require_admin_user

@pytest.fixture(autouse=True)
def override_admin_user():
    # Patch the dependency to always return a dummy admin user
    app.dependency_overrides[require_admin_user] = lambda: types.SimpleNamespace(id=uuid.uuid4(), username="adminuser", role="admin", is_active=True)
    yield
    app.dependency_overrides.pop(require_admin_user, None)

ADMIN_USER = {"username": "adminuser", "password": "AdminPass123!", "role": "admin"}
STAFF_USER = {"username": "staffuser", "password": "StaffPass123!", "role": "staff"}


def test_create_auth_user():
    response = client.post("/api/v1/auth_users/", json=ADMIN_USER)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == ADMIN_USER["username"]
    assert data["role"] == ADMIN_USER["role"]
    assert data["is_active"] is True
    assert "id" in data


def test_get_auth_user():
    # Create user
    response = client.post("/api/v1/auth_users/", json=STAFF_USER)
    user_id = response.json()["id"]
    # Retrieve user by id
    get_resp = client.get(f"/api/v1/auth_users/{user_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["username"] == STAFF_USER["username"]
    assert data["role"] == STAFF_USER["role"]
    assert data["is_active"] is True
    assert data["id"] == user_id


def test_update_auth_user():
    # Create user
    create_resp = client.post("/api/v1/auth_users/", json={"username": "updateuser", "password": "UpdatePass123!", "role": "staff"})
    user_id = create_resp.json()["id"]
    # Update user
    update_payload = {"role": "admin", "is_active": False}
    resp = client.put(f"/api/v1/auth_users/{user_id}", json=update_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"
    assert data["is_active"] is False


def test_delete_auth_user():
    # Create user
    create_resp = client.post("/api/v1/auth_users/", json={"username": "deleteuser", "password": "DeletePass123!", "role": "staff"})
    user_id = create_resp.json()["id"]
    # Delete user
    del_resp = client.delete(f"/api/v1/auth_users/{user_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["ok"] is True
