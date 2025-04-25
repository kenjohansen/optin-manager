"""
models/verification_code.py

SQLAlchemy model for the VerificationCode entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base

class VerificationPurposeEnum(str, enum.Enum):
    """Enumeration for verification purposes."""
    opt_in = "opt-in"
    opt_out = "opt-out"
    preference_change = "preference-change"
    self_service = "self_service"
    verbal_auth = "verbal_auth"

class VerificationStatusEnum(str, enum.Enum):
    """Enumeration for verification status values."""
    pending = "pending"
    verified = "verified"
    expired = "expired"

class VerificationChannelEnum(str, enum.Enum):
    """Enumeration for verification channels."""
    sms = "sms"
    email = "email"

class VerificationCode(Base):
    """
    SQLAlchemy model for verification code records.
    Attributes:
        id (str): Primary key (UUID as string).
        user_id (str): Foreign key to contact ID (deterministic ID).
        code (str): Verification code value.
        channel (str): Channel used (sms/email) - derived from contact_type.
        sent_to (str): Original recipient contact (phone/email) - not stored in DB, used for sending.
        expires_at (datetime): Expiration timestamp.
        verified_at (datetime): When code was verified.
        purpose (str): Purpose of verification (opt-in/opt-out/etc).
        status (str): Verification status (pending/verified/expired).
    """
    __tablename__ = "verification_codes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("contacts.id"), nullable=False)
    code = Column(String, nullable=False)
    channel = Column(String, nullable=True)  # Optional, derived from contact_type
    sent_to = Column(String, nullable=True)  # Optional, for tracking purposes only
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    purpose = Column(String, nullable=False)
    status = Column(String, default=VerificationStatusEnum.pending.value)
