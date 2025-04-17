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
from app.core.database import Base

class VerificationPurposeEnum(str, Enum):
    """Enumeration for verification purposes."""
    opt_in = "opt-in"
    opt_out = "opt-out"
    preference_change = "preference-change"

class VerificationStatusEnum(str, Enum):
    """Enumeration for verification status values."""
    pending = "pending"
    verified = "verified"
    expired = "expired"

class VerificationChannelEnum(str, Enum):
    """Enumeration for verification channels."""
    sms = "sms"
    email = "email"

class VerificationCode(Base):
    """
    SQLAlchemy model for verification code records.
    Attributes:
        id (UUID): Primary key.
        user_id (UUID): Foreign key to user.
        code (str): Verification code value.
        channel (str): Channel used (sms/email).
        sent_to (str): Recipient contact (phone/email).
        expires_at (datetime): Expiration timestamp.
        verified_at (datetime): When code was verified.
        purpose (str): Purpose of verification (opt-in/opt-out/etc).
        status (str): Verification status (pending/verified/expired).
    """
    __tablename__ = "verification_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    code = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    sent_to = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    purpose = Column(String, nullable=False)
    status = Column(String, default=VerificationStatusEnum.pending)
