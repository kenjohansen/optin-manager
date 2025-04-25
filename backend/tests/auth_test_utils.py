"""
auth_test_utils.py

Utility functions for authentication in tests.
"""
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.auth import create_access_token
from app.models.auth_user import AuthUser
from app.crud.auth_user import create_auth_user
from app.schemas.auth_user import AuthUserCreate

def get_test_auth_token(role="admin"):
    """
    Generate a test JWT token with the specified role.
    
    Args:
        role (str): Role to include in the token (admin, support)
        
    Returns:
        str: JWT token
    """
    return create_access_token(data={"sub": f"test-{role}", "scope": role})

def get_auth_headers(role="admin"):
    """
    Get authorization headers with a test token.
    
    Args:
        role (str): Role to include in the token (admin, support)
        
    Returns:
        dict: Headers with Authorization
    """
    token = get_test_auth_token(role)
    return {"Authorization": f"Bearer {token}"}

def create_test_user(db: Session, role="admin"):
    """
    Create a test user in the database.
    
    Args:
        db (Session): Database session
        role (str): Role for the user (admin, support)
        
    Returns:
        AuthUser: Created user
    """
    username = f"test-{role}-{uuid.uuid4().hex[:8]}"
    user_data = AuthUserCreate(
        username=username,
        password=f"Test{role.capitalize()}123!",
        role=role
    )
    return create_auth_user(db, user_data)
