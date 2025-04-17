from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class VerificationPurposeEnum(str, Enum):
    opt_in = "opt-in"
    opt_out = "opt-out"
    preference_change = "preference-change"

class VerificationStatusEnum(str, Enum):
    pending = "pending"
    verified = "verified"
    expired = "expired"

class VerificationChannelEnum(str, Enum):
    sms = "sms"
    email = "email"

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    sent_to = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    purpose = Column(String, nullable=False)
    status = Column(String, default=VerificationStatusEnum.pending)
