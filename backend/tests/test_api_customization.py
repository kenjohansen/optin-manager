import os
import shutil
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import require_admin_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_admin_user():
    app.dependency_overrides[require_admin_user] = lambda: type('User', (), {"id": uuid.uuid4(), "username": "admin", "role": "admin", "is_active": True})()
    yield
    app.dependency_overrides.pop(require_admin_user, None)

@pytest.fixture(scope="module", autouse=True)
def cleanup_uploads():
    # Clean up uploads before and after tests
    upload_dir = "static/uploads"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    yield
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)

def test_get_customization_empty():
    resp = client.get("/api/v1/customization/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["logo_url"] is None
    assert data["primary_color"] is None
    assert data["secondary_color"] is None

def test_update_colors():
    payload = {"primary_color": "#123456", "secondary_color": "#abcdef"}
    resp = client.put("/api/v1/customization/colors", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["primary_color"] == payload["primary_color"]
    assert data["secondary_color"] == payload["secondary_color"]

def test_upload_logo():
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    logo_path = "tests/test_logo.png"
    # Create a dummy logo file
    with open(logo_path, "wb") as f:
        f.write(os.urandom(128))
    with open(logo_path, "rb") as f:
        resp = client.post("/api/v1/customization/logo", files={"file": ("logo.png", f, "image/png")})
    os.remove(logo_path)
    assert resp.status_code == 200
    data = resp.json()
    assert data["logo_url"].startswith("/static/uploads/logo")
    assert data["primary_color"] is not None
    assert data["secondary_color"] is not None

def test_get_customization_with_logo_and_colors():
    resp = client.get("/api/v1/customization/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["logo_url"].startswith("/static/uploads/logo")
    assert data["primary_color"] == "#123456"
    assert data["secondary_color"] == "#abcdef"
