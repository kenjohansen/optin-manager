from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class ConsentStatusEnum(str, Enum):
    opt_in = "opt-in"
    opt_out = "opt-out"
    pending = "pending"

class ConsentChannelEnum(str, Enum):
    sms = "sms"
    email = "email"

class Consent(Base):
    __tablename__ = "consents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    channel = Column(String, nullable=False)
    status = Column(String, default=ConsentStatusEnum.pending)
    consent_timestamp = Column(DateTime(timezone=True))
    revoked_timestamp = Column(DateTime(timezone=True), nullable=True)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verification_codes.id"), nullable=True)
    record = Column(String, nullable=True)  # Encrypted JSON
