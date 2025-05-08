"""
schemas/auth.py

Pydantic schemas for authentication and token handling in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    """
    Schema for JWT authentication token responses.
    
    This schema defines the structure of authentication tokens returned to clients
    after successful login. The token-based authentication approach is essential for
    maintaining stateless authentication in the API, which improves scalability and
    security by not requiring server-side session storage.
    
    The token contains encoded user information and permissions, allowing the system
    to verify the user's identity and access rights with each request without
    querying the database repeatedly.
    """
    access_token: str  # The JWT token containing encoded user information
    token_type: str  # The type of token, typically "bearer"
    expires_in: Optional[int] = 3600  # Token validity period in seconds (1 hour default)

class TokenData(BaseModel):
    """
    Schema for decoded JWT token data.
    
    This schema represents the data extracted from a JWT token during verification.
    It contains the essential user identity information needed to authenticate requests
    and determine permissions. The separation of token data from the full user model
    minimizes the amount of sensitive data stored in the token while still providing
    enough information for authentication and authorization checks.
    """
    username: Optional[str] = None  # Username from the token for identifying the user
    scope: Optional[str] = None  # Permission scope from the token (e.g., "admin", "support")

class PasswordResetRequest(BaseModel):
    """
    Schema for password reset requests.
    
    This schema captures the minimum information needed to initiate a password reset
    process. Using only the username (rather than requiring additional identifying
    information) simplifies the process for users while still maintaining security
    through the subsequent verification steps (typically email verification).
    
    The password reset flow is essential for account recovery and maintenance,
    especially for administrative users who need reliable access to the system.
    """
    username: str  # Username of the account requesting password reset

class ChangePasswordRequest(BaseModel):
    """
    Schema for password change requests from authenticated users.
    
    This schema requires both the current password and new password, which is a
    security best practice for password changes. Requiring the current password
    helps prevent unauthorized password changes if a user's session is compromised
    but the attacker doesn't know the current password.
    
    Regular password changes are encouraged as part of good security hygiene,
    especially for administrative accounts with elevated privileges.
    """
    current_password: str  # Current password for verification
    new_password: str  # New password to set
