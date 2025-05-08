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
    """
    Enumeration for consent status values.
    
    These status values track the user's consent state, which is critical for
    regulatory compliance with privacy laws like GDPR and CCPA. The system
    must maintain accurate records of consent status to determine whether
    communications can be legally sent to a contact.
    """
    opt_in = "opt-in"     # User has explicitly consented to receive communications
    opt_out = "opt-out"  # User has explicitly withdrawn consent
    pending = "pending"  # Consent request has been sent but not yet confirmed

class ConsentChannelEnum(str, enum.Enum):
    """
    Enumeration for consent communication channels.
    
    Different communication channels may have different regulatory requirements
    and user preferences. Tracking consent by channel allows the system to
    respect channel-specific preferences (e.g., a user might consent to email
    but opt out of SMS communications).
    """
    sms = "sms"       # Text message communications
    email = "email"  # Email communications

class Consent(Base):
    """
    SQLAlchemy model for consent records.
    
    The Consent model is the cornerstone of the OptIn Manager system, tracking
    explicit user consent for specific communication types. This model maintains
    the complete consent lifecycle, from initial opt-in to potential opt-out,
    with timestamps for audit trails. This granular consent tracking is essential
    for compliance with privacy regulations worldwide that require proof of
    explicit, purpose-specific consent.
    
    Attributes:
        id (UUID): Primary key for uniquely identifying each consent record.
        user_id (UUID): Foreign key to the contact who provided consent, enabling
                      user-centric consent management and reporting.
        optin_id (UUID): Foreign key to the specific opt-in program this consent
                       relates to, supporting granular purpose-specific consent.
        channel (str): Communication channel this consent applies to (sms/email),
                     allowing channel-specific consent preferences.
        status (str): Current consent status (pending/opt-in/opt-out), the core
                    indicator of whether communications are permitted.
        consent_timestamp (datetime): When consent was given, critical for
                                    compliance audit trails and expiration tracking.
        revoked_timestamp (datetime): When consent was revoked, if applicable,
                                    essential for compliance documentation.
        verification_id (UUID): Reference to the verification code used to confirm
                              consent, providing proof of verification.
        record (str): Encrypted JSON record containing additional consent metadata
                    such as IP address, user agent, and consent text version.
        notes (str): Optional freeform notes provided by the contact during the
                   consent process, capturing additional context.
    """
    __tablename__ = "consents"
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    """
    Unique identifier for the consent record using UUID format stored as string.
    UUIDs prevent ID collisions and support distributed systems and data migrations.
    """
    
    user_id = Column(UUID, ForeignKey("contacts.id"), nullable=False)
    """
    Reference to the contact who provided this consent. This relationship is
    required as consent must always be tied to a specific individual for
    compliance and tracking purposes.
    """
    
    optin_id = Column(UUID, ForeignKey("optins.id"), nullable=True)
    """
    Reference to the specific opt-in program this consent applies to. This can be
    nullable to support global opt-out scenarios where a user withdraws from all
    communications regardless of specific program.
    """
    
    channel = Column(String, nullable=False)
    """
    The communication channel this consent applies to (e.g., email, SMS).
    Different channels may have different regulatory requirements and user
    preferences, so tracking consent by channel is essential.
    """
    
    status = Column(String, default=ConsentStatusEnum.pending.value)
    """
    Current consent status (opt-in, opt-out, pending). This is the core field
    that determines whether communications can be sent to the user for this
    specific opt-in program and channel.
    """
    
    consent_timestamp = Column(DateTime(timezone=True))
    """
    When consent was given by the user. This timestamp is critical for compliance
    with regulations that require proof of when consent was obtained and for
    implementing consent expiration policies.
    """
    
    revoked_timestamp = Column(DateTime(timezone=True), nullable=True)
    """
    When consent was revoked by the user, if applicable. This supports the
    right to withdraw consent and provides an audit trail of the complete
    consent lifecycle.
    """
    
    verification_id = Column(UUID, ForeignKey("verification_codes.id"), nullable=True)
    """
    Reference to the verification code used to confirm this consent, if applicable.
    This provides proof that the consent was verified through a confirmation process,
    which is important for demonstrating that consent was freely given.
    """
    
    record = Column(String, nullable=True)  # Encrypted JSON
    """
    Encrypted JSON record containing additional metadata about the consent,
    such as IP address, user agent, and the specific version of consent text
    that was shown to the user. This supports detailed audit requirements.
    """
    
    notes = Column(String, nullable=True)  # Freeform notes from contact
    """
    Optional freeform notes provided by the contact during the consent process.
    This field captures any additional context or conditions the user may have
    specified when providing or withdrawing consent.
    """
