"""
tests/test_api_customization_additional.py

Additional tests for the customization API endpoints.
"""
import os
import pytest
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.deps import require_admin_user
from app.models.customization import Customization
import uuid
import shutil
from io import BytesIO

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_admin_user():
    app.dependency_overrides[require_admin_user] = lambda: type('User', (), {"id": str(uuid.uuid4()), "username": "admin", "role": "admin", "is_active": True})()
    yield
    app.dependency_overrides.pop(require_admin_user, None)

@pytest.fixture(scope="module", autouse=True)
def cleanup_uploads():
    # Clean up uploads before and after tests
    upload_dir = "static/uploads"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
    yield
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)

def test_save_customization_complete(db_session: Session):
    """Test saving all customization settings together."""
    # Ensure the upload directory exists
    import os
    os.makedirs("static/uploads", exist_ok=True)
    # Create a test logo file
    logo_content = b"fake_image_content"
    logo = BytesIO(logo_content)
    
    # Define the form data
    form_data = {
        "primary": "#FF5733",
        "secondary": "#33FF57",
        "company_name": "Test Company Name",
        "privacy_policy_url": "https://example.com/privacy",
        "email_provider": "aws_ses",
        "sms_provider": "twilio"
    }
    
    # Make the multipart/form-data request with both file and form fields
    files = {
        "logo": ("test_logo.png", logo, "image/png")
    }
    
    # Send the request
    response = client.post(
        "/api/v1/customization/",
        data=form_data,
        files=files
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    
    # Verify all fields were saved correctly
    assert data["primary_color"] == "#FF5733"
    assert data["secondary_color"] == "#33FF57"
    assert data["company_name"] == "Test Company Name"
    assert data["privacy_policy_url"] == "https://example.com/privacy"
    assert data["email_provider"] == "aws_ses"
    assert data["sms_provider"] == "twilio"
    assert data["logo_url"] is not None
    
    # Verify the logo file was saved
    logo_path = data["logo_url"]
    # If logo_url is a URL, extract the local path
    if logo_path.startswith("/"):
        logo_path = logo_path.lstrip("/")
    # Compute absolute path using backend logic
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    abs_logo_path = os.path.join(BASE_DIR, logo_path)
    assert os.path.exists(abs_logo_path), f"Logo file does not exist at {abs_logo_path}"
    
    # Verify database record
    db_customization = db_session.query(Customization).first()
    assert db_customization is not None
    assert db_customization.primary_color == "#FF5733"
    assert db_customization.secondary_color == "#33FF57"
    assert db_customization.company_name == "Test Company Name"
    assert db_customization.privacy_policy_url == "https://example.com/privacy"
    assert db_customization.email_provider == "aws_ses"
    assert db_customization.sms_provider == "twilio"
    assert db_customization.logo_path is not None

def test_save_customization_invalid_logo_type(db_session: Session):
    """Test saving customization with an invalid logo file type."""
    # Create a fake text file
    text_content = b"This is not an image"
    text_file = BytesIO(text_content)
    
    # Define form data
    form_data = {
        "company_name": "Test Company"
    }
    
    # Make the request with an invalid file type
    files = {
        "logo": ("invalid.txt", text_file, "text/plain")
    }
    
    # Send the request
    response = client.post(
        "/api/v1/customization/",
        data=form_data,
        files=files
    )
    
    # Check that it returns an error
    assert response.status_code == 500
    data = response.json()
    assert "Invalid file type" in data["detail"]
