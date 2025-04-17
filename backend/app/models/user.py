from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class UserStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=True, unique=True)
    phone = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default=UserStatusEnum.active)
