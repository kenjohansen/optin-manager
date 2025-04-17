import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
import pytest

client = TestClient(app)

import types
from app.core.deps import require_admin_user

@pytest.fixture(autouse=True)
def override_admin_user():
    # Patch the dependency to always return a dummy admin user
    app.dependency_overrides[require_admin_user] = lambda: types.SimpleNamespace(id=uuid.uuid4(), username="adminuser", role="admin", is_active=True)
    yield
    app.dependency_overrides.pop(require_admin_user, None)

# Fixtures for test campaign data
def sample_campaign_payload():
    return {
        "name": f"TestCampaign_{uuid.uuid4().hex[:8]}",
        "type": "transactional",
        "status": "active"
    }

def test_create_campaign():
    payload = sample_campaign_payload()
    response = client.post("/api/v1/campaigns/", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["type"] == payload["type"]
    assert data["status"] == payload["status"]
    assert "id" in data
    assert "created_at" in data
    global campaign_id
    campaign_id = data["id"]

def test_read_campaign():
    payload = sample_campaign_payload()
    create_resp = client.post("/api/v1/campaigns/", json=payload)
    assert create_resp.status_code == 200
    campaign = create_resp.json()
    response = client.get(f"/api/v1/campaigns/{campaign['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == campaign["id"]
    assert data["name"] == campaign["name"]
    assert data["type"] == campaign["type"]
    assert data["status"] == campaign["status"]

def test_update_campaign():
    payload = sample_campaign_payload()
    create_resp = client.post("/api/v1/campaigns/", json=payload)
    assert create_resp.status_code == 200
    campaign = create_resp.json()
    update_payload = {
        "name": campaign["name"] + "_updated",
        "type": "promotional",
        "status": "paused"
    }
    response = client.put(f"/api/v1/campaigns/{campaign['id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == campaign["id"]
    assert data["name"] == update_payload["name"]
    assert data["type"] == update_payload["type"]
    assert data["status"] == update_payload["status"]

def test_delete_campaign():
    payload = sample_campaign_payload()
    create_resp = client.post("/api/v1/campaigns/", json=payload)
    assert create_resp.status_code == 200
    campaign = create_resp.json()
    response = client.delete(f"/api/v1/campaigns/{campaign['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Confirm deletion
    get_resp = client.get(f"/api/v1/campaigns/{campaign['id']}")
    assert get_resp.status_code == 404
