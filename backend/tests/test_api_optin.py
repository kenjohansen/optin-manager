"""
test_api_optin.py

Unit tests for the OptIn API endpoints.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.optin import OptInTypeEnum, OptInStatusEnum
from tests.auth_test_utils import get_auth_headers, create_test_user

client = TestClient(app)

def test_create_and_get_optin(db_session: Session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create unique test data
    data = {
        "name": f"Test Opt-In {uuid.uuid4().hex[:8]}",
        "type": "promotional",
        "description": "Test Description",
        "status": "active"
    }
    
    # Create
    resp = client.post("/api/v1/optins/", json=data, headers=headers)
    assert resp.status_code == 200, f"Failed to create optin: {resp.text}"
    
    optin = resp.json()
    assert optin["name"] == data["name"]
    assert optin["type"] == data["type"]
    assert optin["status"] == data["status"]
    assert "id" in optin, "Response should include an ID"
    
    # Get
    get_resp = client.get(f"/api/v1/optins/{optin['id']}", headers=headers)
    assert get_resp.status_code == 200, f"Failed to get optin: {get_resp.text}"
    
    get_optin = get_resp.json()
    assert get_optin["id"] == optin["id"]
    assert get_optin["name"] == data["name"]
    
    # List
    list_resp = client.get("/api/v1/optins/", headers=headers)
    assert list_resp.status_code == 200, f"Failed to list optins: {list_resp.text}"
    assert any(o["id"] == optin["id"] for o in list_resp.json())

def test_update_optin(db_session: Session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create unique test data
    data = {
        "name": f"To Update {uuid.uuid4().hex[:8]}", 
        "type": "transactional", 
        "status": "active"
    }
    
    # Create
    resp = client.post("/api/v1/optins/", json=data, headers=headers)
    assert resp.status_code == 200, f"Failed to create optin: {resp.text}"
    
    optin = resp.json()
    optin_id = optin["id"]
    
    # Update
    update = {"name": f"Updated Name {uuid.uuid4().hex[:8]}", "description": "Updated description"}
    up_resp = client.put(f"/api/v1/optins/{optin_id}", json=update, headers=headers)
    assert up_resp.status_code == 200, f"Failed to update optin: {up_resp.text}"
    
    up_optin = up_resp.json()
    assert up_optin["name"] == update["name"]
    assert up_optin["description"] == update["description"]
    assert up_optin["status"] == "active"  # Status should remain unchanged

def test_optin_status_management(db_session: Session):
    # Get admin auth headers
    headers = get_auth_headers(role="admin")
    
    # Create unique test data
    data = {
        "name": f"Status Test {uuid.uuid4().hex[:8]}", 
        "type": "promotional", 
        "status": "active"
    }
    
    # Create
    resp = client.post("/api/v1/optins/", json=data, headers=headers)
    assert resp.status_code == 200, f"Failed to create optin: {resp.text}"
    
    optin = resp.json()
    optin_id = optin["id"]
    
    # 1. Pause the opt-in
    pause_resp = client.put(f"/api/v1/optins/{optin_id}/pause", headers=headers)
    assert pause_resp.status_code == 200, f"Failed to pause optin: {pause_resp.text}"
    
    paused_optin = pause_resp.json()["optin"]
    assert paused_optin["status"] == "paused"
    
    # Verify status in a separate get request
    get_resp = client.get(f"/api/v1/optins/{optin_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "paused"
    
    # 2. Resume the opt-in
    resume_resp = client.put(f"/api/v1/optins/{optin_id}/resume", headers=headers)
    assert resume_resp.status_code == 200, f"Failed to resume optin: {resume_resp.text}"
    
    resumed_optin = resume_resp.json()["optin"]
    assert resumed_optin["status"] == "active"
    
    # 3. Archive the opt-in
    archive_resp = client.put(f"/api/v1/optins/{optin_id}/archive", headers=headers)
    assert archive_resp.status_code == 200, f"Failed to archive optin: {archive_resp.text}"
    
    archived_optin = archive_resp.json()["optin"]
    assert archived_optin["status"] == "archived"
    
    # Verify the opt-in still exists but is archived
    get_resp = client.get(f"/api/v1/optins/{optin_id}", headers=headers)
    assert get_resp.status_code == 200, "Archived optin should still exist"
    assert get_resp.json()["status"] == "archived"
