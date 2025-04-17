"""
models/consent.py

SQLAlchemy model for the Consent entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class ConsentStatusEnum(str, Enum):
    """Enumeration for consent status values."""
    opt_in = "opt-in"
    opt_out = "opt-out"
    pending = "pending"

class ConsentChannelEnum(str, Enum):
    """Enumeration for consent channels."""
    sms = "sms"
    email = "email"

class Consent(Base):
    """
    SQLAlchemy model for consent records.
    Attributes:
        id (UUID): Primary key.
        user_id (UUID): Foreign key to user.
        campaign_id (UUID): Foreign key to campaign.
        channel (str): Channel for consent (sms/email).
        status (str): Consent status (pending/opt-in/opt-out).
        consent_timestamp (datetime): When consent was given.
        revoked_timestamp (datetime): When consent was revoked.
        verification_id (UUID): Foreign key to verification code.
        record (str): Encrypted JSON record.
    """
    __tablename__ = "consents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    channel = Column(String, nullable=False)
    status = Column(String, default=ConsentStatusEnum.pending)
    consent_timestamp = Column(DateTime(timezone=True))
    revoked_timestamp = Column(DateTime(timezone=True), nullable=True)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verification_codes.id"), nullable=True)
    record = Column(String, nullable=True)  # Encrypted JSON
