from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class MessageTemplateChannelEnum(str, Enum):
    sms = "sms"
    email = "email"

class MessageTemplate(Base):
    __tablename__ = "message_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
