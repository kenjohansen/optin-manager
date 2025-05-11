"""
test_main.py

Tests for the main FastAPI application features including routes and middleware.
"""

from fastapi.testclient import TestClient
from app.main import app

# Create a test client
client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint returns OK status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_favicon_endpoint():
    """Test the favicon endpoint returns the favicon file."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")

def test_docs_endpoint_redirect():
    """Test the docs endpoint redirects to Swagger UI."""
    response = client.get("/docs", follow_redirects=False)
    assert response.status_code == 200 or response.status_code == 302
    
    # If it's a redirect, check it goes to the right place
    if response.status_code == 302:
        assert "swagger-ui" in response.headers["location"]

def test_redoc_endpoint():
    """Test the redoc endpoint for API documentation."""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_static_files():
    """Test the static files are served correctly."""
    response = client.get("/static/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")

def test_validation_error_handler():
    """Test the validation error handler returns proper 422 errors."""
    # Use an endpoint we know requires validation - login requires username/password
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
    assert "detail" in response.json()
