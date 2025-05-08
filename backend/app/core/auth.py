"""
core/auth.py

Authentication and JWT utility functions for OptIn Manager backend.

This module provides the core authentication functionality for the OptIn Manager system,
including password hashing, JWT token generation and validation, and user authentication.
It supports the role-based access control system where users can have different roles
(Admin, Support) with varying permission levels.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.database import get_db

# Secret key and algorithm for JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using bcrypt.
    
    This function is essential for secure authentication, allowing the system to
    verify user passwords without storing them in plaintext. It uses the bcrypt
    hashing algorithm, which is designed specifically for password hashing and
    includes built-in salt to protect against rainbow table attacks.
    
    Args:
        plain_password (str): The plaintext password provided during login
        hashed_password (str): The stored hashed password from the database
        
    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a secure hash of a password using bcrypt.
    
    This function is used when creating or updating user passwords, ensuring that
    passwords are never stored in plaintext. The bcrypt algorithm automatically
    generates and incorporates a salt, making each hash unique even for identical
    passwords and protecting against rainbow table attacks.
    
    Args:
        password (str): The plaintext password to hash
        
    Returns:
        str: The secure bcrypt hash of the password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token for authenticated users.
    
    This function generates a secure JSON Web Token (JWT) that serves as the
    authentication credential for users after they log in. The token contains
    the user's identity and role information, along with an expiration time.
    
    As noted in the memories, if a token expires, the user may see the dashboard
    but the nav bar may show unauthorized menu options, indicating a potential
    auth state bug that should be addressed.
    
    Args:
        data (dict): The payload to encode in the token, typically containing
                   the user's username ('sub') and role information
        expires_delta (Optional[timedelta]): Custom expiration time delta;
                                           if None, uses the default (60 minutes)
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """
    Decode and validate a JWT access token.
    
    This function verifies that a token is valid (properly signed and not expired)
    and returns its payload. If the token is invalid or expired, it raises an
    HTTP exception with a 401 Unauthorized status code.
    
    This validation is essential for protecting secured endpoints and ensuring
    that only authenticated users with valid tokens can access protected resources.
    
    Args:
        token (str): The JWT token to decode and validate
        
    Returns:
        dict: The decoded token payload containing user information
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    """
    Get the current authenticated user from a JWT token.
    
    This function is used as a dependency in protected API endpoints to authenticate
    the request and retrieve the current user. It validates the JWT token, extracts
    the username, and looks up the corresponding user in the database.
    
    As noted in the memories, the system supports two roles for authenticated users:
    - Admin: Can create campaigns/products and manage authenticated users
    - Support: Can view all pages but cannot create or manage resources
    
    This function is essential for implementing role-based access control, as it
    provides the user object with role information that can be used for permission
    checks in the API endpoints.
    
    Args:
        token (str): The JWT token from the Authorization header
        db (Session): SQLAlchemy database session
        
    Returns:
        AuthUser: The authenticated user object from the database
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    from app.crud.auth_user import get_auth_user_by_username
    user = get_auth_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user
