"""
core/deps.py

Dependency functions for authentication and authorization in OptIn Manager backend.

This module provides FastAPI dependency functions for implementing role-based access
control in the OptIn Manager system. It enables the enforcement of permission
requirements on API endpoints based on user roles.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.auth import TokenData
from app.core.auth import oauth2_scheme

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# Dependency to get the current user (admin or contact)
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Validate JWT token and extract user information.
    
    This function is the foundation of the authentication system, validating
    the JWT token provided in the request and extracting the user identity and
    scope (role). It's used as a dependency in other permission-checking functions.
    
    As noted in the memories, the system supports two roles for authenticated users:
    - Admin: Can create campaigns/products and manage authenticated users
    - Support: Can view all pages but cannot create or manage resources
    
    Additionally, there's a 'contact' scope for non-authenticated users who have
    verified their identity through the verification code process, which is used
    for the Opt-Out workflow.
    
    Args:
        token (str): JWT token from the Authorization header
        
    Returns:
        TokenData: Object containing username and scope (role)
        
    Raises:
        HTTPException: 401 Unauthorized if token is invalid or missing required claims
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        scope: str = payload.get("scope")
        if username is None or scope is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(username=username, scope=scope)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to require admin scope
def require_admin_user(current_user: TokenData = Depends(get_current_user)):
    """
    Dependency to require admin scope (admin role only).
    
    This function enforces that only users with the 'admin' role can access
    the endpoint. As noted in the memories, Admin users can create campaigns,
    products, and manage authenticated users.
    
    This dependency should be used on endpoints that perform sensitive operations
    like user management, system configuration, or creating/modifying opt-in programs.
    
    Args:
        current_user (TokenData): User information from the JWT token
        
    Returns:
        TokenData: The validated user information if authorized
        
    Raises:
        HTTPException: 403 Forbidden if user doesn't have admin role
    """
    if current_user.scope != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# Dependency to require support or admin scope
def require_support_user(current_user: TokenData = Depends(get_current_user)):
    """
    Dependency to require support or admin scope (support or admin roles).
    
    This function enforces that users must have either 'support' or 'admin' role
    to access the endpoint. As noted in the memories, Support users can view all
    pages but cannot create campaigns/products or manage users.
    
    This dependency should be used on endpoints that provide read access to system
    data but don't perform sensitive operations. It allows both support staff and
    administrators to access the endpoint.
    
    Args:
        current_user (TokenData): User information from the JWT token
        
    Returns:
        TokenData: The validated user information if authorized
        
    Raises:
        HTTPException: 403 Forbidden if user doesn't have support or admin role
    """
    if current_user.scope not in ("admin", "support"):
        raise HTTPException(status_code=403, detail="Support or admin privileges required")
    return current_user

# Dependency to require contact scope (verified contact)
def require_verified_contact(current_user: TokenData = Depends(get_current_user)):
    """
    Dependency to require contact scope (verified contact).
    
    This function enforces that the user must have the 'contact' scope to access
    the endpoint. This scope is assigned to non-authenticated users who have
    verified their identity through the verification code process.
    
    As noted in the memories, this is essential for the Opt-Out workflow, which
    requires sending a verification code, verifying the code, and then allowing
    the user to manage their preferences. This dependency ensures that only
    verified contacts can access preference management endpoints.
    
    Args:
        current_user (TokenData): User information from the JWT token
        
    Returns:
        TokenData: The validated user information if authorized
        
    Raises:
        HTTPException: 403 Forbidden if user doesn't have contact scope
    """
    if current_user.scope != "contact":
        raise HTTPException(status_code=403, detail="Contact verification required")
    return current_user
