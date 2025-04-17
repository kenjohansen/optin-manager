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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default=AuthUserRoleEnum.staff)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
