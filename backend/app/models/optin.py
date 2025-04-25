"""
models/optin.py

SQLAlchemy model for the OptIn entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func
# Use String type for UUID in SQLite
from sqlalchemy import String as UUID
import uuid
from app.core.database import Base
import enum

class OptInTypeEnum(str, enum.Enum):
    promotional = "promotional"
    transactional = "transactional"
    alert = "alert"

class OptInStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"
    archived = "archived"
    closed = "closed"

class OptIn(Base):
    __tablename__ = "optins"
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(Enum(OptInTypeEnum), default=OptInTypeEnum.transactional, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(OptInStatusEnum), default=OptInStatusEnum.active, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
