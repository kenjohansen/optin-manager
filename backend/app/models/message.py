from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class MessageStatusEnum(str, Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"

class MessageChannelEnum(str, Enum):
    sms = "sms"
    email = "email"

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("message_templates.id"), nullable=True)
    channel = Column(String, nullable=False)
    content = Column(String, nullable=False)  # Encrypted
    status = Column(String, default=MessageStatusEnum.pending)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivery_status = Column(String, nullable=True)  # JSON string
