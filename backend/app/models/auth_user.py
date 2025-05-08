"""
models/auth_user.py

SQLAlchemy model for authentication users (admin/staff/service accounts) in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class AuthUserRoleEnum(str, Enum):
    """
    Enumeration of authenticated user roles for access control.
    
    The system supports different user roles with varying levels of permissions.
    As noted in the memories, the system primarily supports two roles: Admin (full access)
    and Support (read-only), with different capabilities for each role. The service
    role is reserved for automated service accounts that may need API access.
    """
    admin = "admin"    # Full access to all features including user management
    staff = "staff"    # Read-only access to most features (Support role)
    service = "service"  # Limited API access for automated services

class AuthUser(Base):
    """
    SQLAlchemy model representing authenticated users in the system.
    
    The AuthUser model represents users who can log into the system with different
    permission levels. This is distinct from the Contact model, which represents
    individuals who may provide consent but don't have system access. This separation
    is critical for security and access control, ensuring that only authorized users
    can access administrative functions.
    
    As noted in the memories, the system supports two main roles:
    - Admin: Can create campaigns/products and manage authenticated users
    - Support: Can view all pages but cannot create or manage resources
    """
    __tablename__ = "auth_users"
    
    # Use String type for ID to be compatible with both UUID and integer formats
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    """
    Unique identifier for the user using UUID format stored as string.
    UUIDs prevent ID collisions and support distributed systems and data migrations.
    """
    
    username = Column(String, unique=True, nullable=False)
    """
    Unique username for login purposes. This must be unique across the system
    to prevent authentication conflicts and ensure security.
    """
    
    password_hash = Column(String, nullable=False)
    """
    Hashed password for secure authentication. Raw passwords are never stored
    in the database for security reasons.
    """
    
    name = Column(String, nullable=True)
    """
    Full name of the user for display purposes. This is optional as some
    service accounts may not have an associated person.
    """
    
    email = Column(String, nullable=True)
    """
    Email address for contact and notifications. This is optional but
    recommended for password reset functionality.
    """
    
    role = Column(String, default=AuthUserRoleEnum.staff)
    """
    User role that determines permissions (admin/staff/service). The default
    is staff (Support role) which has read-only access.
    """
    
    is_active = Column(Boolean, default=True)
    """
    Whether the user account is currently active. Inactive accounts cannot
    log in but are preserved for audit purposes rather than being deleted.
    """
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    """
    Timestamp when the user account was created. This is important for
    audit trails and security monitoring.
    """
