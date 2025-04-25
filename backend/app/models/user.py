"""
models/user.py

SQLAlchemy model for the User entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base
import enum

class UserStatusEnum(str, enum.Enum):
    """Enumeration for user status values."""
    active = "active"
    inactive = "inactive"

class ContactTypeEnum(str, enum.Enum):
    """Enumeration for contact type values."""
    email = "email"
    phone = "phone"

class Contact(Base):
    """
    SQLAlchemy model for contact records (opt-in/consent, no authentication).
    Attributes:
        id (String): Primary key - deterministic ID generated from contact value.
        encrypted_value (str): Encrypted contact value (email or phone).
        contact_type (str): Type of contact (email/phone).
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        status (str): Contact status (active/inactive).
        is_admin (bool): Whether the contact has admin privileges.
        is_staff (bool): Whether the contact has staff privileges.
        comment (str): Stores opt-out comment from contact.
    """
    __tablename__ = "contacts"
    id = Column(String, primary_key=True)  # Deterministic ID from contact value
    encrypted_value = Column(String, nullable=False, unique=True)  # Encrypted email or phone
    contact_type = Column(String, nullable=False)  # 'email' or 'phone'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default=UserStatusEnum.active.value)
    is_admin = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    comment = Column(String, nullable=True)  # Stores opt-out comment from contact
