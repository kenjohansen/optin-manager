"""
models/message.py

SQLAlchemy model for the Message entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class MessageStatusEnum(str, Enum):
    """Enumeration for message status values."""
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"

class MessageChannelEnum(str, Enum):
    """Enumeration for message channels."""
    sms = "sms"
    email = "email"

class Message(Base):
    """
    SQLAlchemy model for message records.
    Attributes:
        id (UUID): Primary key.
        user_id (UUID): Foreign key to user.
        campaign_id (UUID): Foreign key to campaign.
        template_id (UUID): Foreign key to message template.
        channel (str): Message channel (sms/email).
        content (str): Encrypted message content.
        status (str): Message status (pending/sent/delivered/failed).
        sent_at (datetime): When message was sent.
        delivery_status (str): Delivery status JSON string.
    """
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("message_templates.id"), nullable=True)
    channel = Column(String, nullable=False)
    content = Column(String, nullable=False)  # Encrypted
    status = Column(String, default=MessageStatusEnum.pending)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivery_status = Column(String, nullable=True)  # JSON string
