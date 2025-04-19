"""
models/user.py

SQLAlchemy model for the User entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class UserStatusEnum(str, Enum):
    """Enumeration for user status values."""
    active = "active"
    inactive = "inactive"

class Contact(Base):
    """
    SQLAlchemy model for contact records (opt-in/consent, no authentication).
    Attributes:
        id (UUID): Primary key.
        email (str): Contact email address.
        phone (str): Contact phone number.
        created_at (datetime): Creation timestamp.
        status (str): Contact status (active/inactive).
    """
    __tablename__ = "contacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=True, unique=True)
    phone = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default=UserStatusEnum.active)
    is_admin = Column(String, default="false")  # Will change to Boolean in Alembic migration
    is_staff = Column(String, default="false")  # Will change to Boolean in Alembic migration
    comment = Column(String, nullable=True)  # Stores opt-out comment from contact
