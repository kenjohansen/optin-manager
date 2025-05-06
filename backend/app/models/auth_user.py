"""
models/auth_user.py

SQLAlchemy model for authentication users (admin/staff/service accounts) in the OptIn Manager backend.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class AuthUserRoleEnum(str, Enum):
    admin = "admin"
    staff = "staff"
    service = "service"

class AuthUser(Base):
    __tablename__ = "auth_users"
    # Use String type for ID to be compatible with both UUID and integer formats
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    # Add name and email fields
    name = Column(String, nullable=True)  # Full name of the user
    email = Column(String, nullable=True)  # Email address for contact
    role = Column(String, default=AuthUserRoleEnum.staff)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
