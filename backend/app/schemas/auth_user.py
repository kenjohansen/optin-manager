"""
schemas/auth_user.py

Pydantic schemas for authentication users (admin/staff/service accounts).

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, Field
from typing import Optional
import uuid

class AuthUserBase(BaseModel):
    """
    Base schema for authenticated user data with common fields.
    
    The AuthUser schema represents users who can log into the system with different
    permission levels. This is distinct from the Contact model, which represents
    individuals who may provide consent but don't have system access. This separation
    is critical for security and access control, ensuring that only authorized users
    can access administrative functions.
    
    The system supports two roles as noted in the memories: Admin (full access) and
    Support (read-only), with different capabilities for each role.
    """
    username: str  # Unique identifier for login purposes
    name: Optional[str] = None  # Full name for display purposes
    email: Optional[str] = None  # Email for notifications and password resets
    role: str = "staff"  # Role determines permissions (admin/support)
    is_active: bool = True  # Whether the user account is currently active

class AuthUserCreate(AuthUserBase):
    """
    Schema for creating a new authenticated user.
    
    This schema extends AuthUserBase to include the password field required for
    initial user creation. The password is never stored in plain text but is
    hashed before storage, which is essential for security. This schema is used
    only by administrators when creating new system users.
    """
    password: str  # Plain text password that will be hashed before storage

class AuthUserUpdate(BaseModel):
    """
    Schema for updating an existing authenticated user.
    
    This schema makes all fields optional, allowing partial updates to user records.
    This is particularly important for password changes, which should be handled
    separately from other profile updates for security reasons. The ability to
    update the role and active status enables administrators to manage user
    permissions and access without creating new accounts.
    """
    password: Optional[str] = None  # New password (will be hashed before storage)
    name: Optional[str] = None  # Updated name if changing
    email: Optional[str] = None  # Updated email if changing
    role: Optional[str] = None  # Updated role if changing permissions
    is_active: Optional[bool] = None  # Updated active status if enabling/disabling

class AuthUserOut(AuthUserBase):
    """
    Schema for returning authenticated user data via API responses.
    
    This schema extends AuthUserBase to include system-generated fields like ID and
    creation timestamp. Notably, it does not include the password field, as passwords
    should never be returned in API responses, even in hashed form. This schema is
    used for user profile information and user management interfaces.
    """
    id: str  # Unique system identifier for this user
    created_at: Optional[str] = None  # When the user account was created
