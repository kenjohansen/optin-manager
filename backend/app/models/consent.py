"""
models/consent.py

SQLAlchemy model for the Consent entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, func
import enum
# Use String type for UUID in SQLite
from sqlalchemy import String as UUID
import uuid
from app.core.database import Base

class ConsentStatusEnum(str, enum.Enum):
    """Enumeration for consent status values."""
    opt_in = "opt-in"
    opt_out = "opt-out"
    pending = "pending"

class ConsentChannelEnum(str, enum.Enum):
    """Enumeration for consent channels."""
    sms = "sms"
    email = "email"

class Consent(Base):
    """
    SQLAlchemy model for consent records.
    Attributes:
        id (UUID): Primary key.
        user_id (UUID): Foreign key to user.
        optin_id (UUID): Foreign key to optin.
        channel (str): Channel for consent (sms/email).
        status (str): Consent status (pending/opt-in/opt-out).
        consent_timestamp (datetime): When consent was given.
        revoked_timestamp (datetime): When consent was revoked.
        verification_id (UUID): Foreign key to verification code.
        record (str): Encrypted JSON record.
    """
    __tablename__ = "consents"
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID, ForeignKey("contacts.id"), nullable=False)
    optin_id = Column(UUID, ForeignKey("optins.id"), nullable=True)
    channel = Column(String, nullable=False)
    status = Column(String, default=ConsentStatusEnum.pending.value)
    consent_timestamp = Column(DateTime(timezone=True))
    revoked_timestamp = Column(DateTime(timezone=True), nullable=True)
    verification_id = Column(UUID, ForeignKey("verification_codes.id"), nullable=True)
    record = Column(String, nullable=True)  # Encrypted JSON
    notes = Column(String, nullable=True)  # Freeform notes from contact
