"""
models/message_template.py

SQLAlchemy model for the MessageTemplate entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class MessageTemplateChannelEnum(str, Enum):
    """Enumeration for message template channels."""
    sms = "sms"
    email = "email"

class MessageTemplate(Base):
    """
    SQLAlchemy model for message template records.
    Attributes:
        id (UUID): Primary key.
        name (str): Template name.
        content (str): Template content.
        channel (str): Communication channel (sms/email).
        created_at (datetime): Creation timestamp.
    """
    __tablename__ = "message_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
