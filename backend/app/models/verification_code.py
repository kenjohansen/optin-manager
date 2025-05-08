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
    """
    Enumeration for verification purposes.
    
    Different verification purposes may have different regulatory requirements and
    retention policies. Tracking the specific purpose of each verification code
    ensures that the system can apply the appropriate rules and maintain proper
    audit trails for each type of consent action.
    
    This is particularly important for demonstrating compliance with regulations
    like GDPR and CCPA, which require evidence of explicit consent for different
    types of data processing activities.
    """
    opt_in = "opt-in"                  # Verifying consent to receive communications
    opt_out = "opt-out"                # Verifying request to withdraw consent
    preference_change = "preference-change"  # Verifying changes to communication preferences
    self_service = "self_service"      # Verifying identity for self-service portal access
    verbal_auth = "verbal_auth"        # Verifying verbal consent provided via phone

class VerificationStatusEnum(str, enum.Enum):
    """
    Enumeration for verification status values.
    
    Tracking the status of verification codes is essential for security and compliance.
    It prevents codes from being used multiple times or after expiration, which could
    lead to unauthorized access or fraudulent consent records.
    
    The status lifecycle (pending → verified/expired) provides a clear audit trail
    of the verification process, which may be required for regulatory compliance.
    """
    pending = "pending"    # Code has been sent but not yet verified
    verified = "verified"  # Code has been successfully verified
    expired = "expired"    # Code has expired without being verified

class VerificationChannelEnum(str, enum.Enum):
    """
    Enumeration for verification channels.
    
    Different verification channels have different security characteristics and
    regulatory requirements. Tracking which channel was used for verification
    helps demonstrate compliance with channel-specific regulations and security
    best practices.
    
    For example, some high-risk actions might require verification through multiple
    channels for enhanced security (multi-factor authentication).
    """
    sms = "sms"     # Verification via text message
    email = "email" # Verification via email message

class VerificationCode(Base):
    """
    SQLAlchemy model for verification code records.
    
    The VerificationCode model is a critical security and compliance component that
    manages the verification process for consent actions. Verification codes provide
    proof that the individual who claims to own a contact method (email/phone) actually
    has access to it, which is essential for establishing valid consent under regulations
    like GDPR and CCPA.
    
    This verification process helps prevent fraudulent opt-ins and unauthorized
    preference changes, protecting both users and the organization. It creates an
    audit trail that demonstrates the organization took reasonable steps to verify
    the identity of individuals before processing their consent.
    
    As noted in the memories, the Opt-Out workflow requires sending a verification
    code, verifying that code, and then allowing the user to manage their preferences.
    This ensures that only the actual owner of a contact method can modify consent
    settings associated with it.
    
    Attributes:
        id (str): Primary key (UUID as string) that uniquely identifies each
                verification code record for tracking and auditing.
        
        user_id (str): Foreign key to the contact record, linking this verification
                     code to a specific individual. This is essential for tracking
                     who the verification code was issued to.
        
        code (str): The actual verification code value that the user must provide
                  to prove their identity. This should be a secure, randomly
                  generated value of sufficient complexity.
        
        channel (str): The communication channel used to send the code (sms/email).
                     This is derived from the contact type and affects the format
                     and delivery method of the code.
        
        sent_to (str): The original recipient contact information (phone/email).
                     This may be stored in masked form for audit purposes while
                     protecting the actual contact details.
        
        expires_at (datetime): When the code will expire, which is essential for
                            security. Short expiration times reduce the window of
                            opportunity for unauthorized use.
        
        verified_at (datetime): Timestamp when the code was successfully verified,
                             providing an audit trail of when verification occurred.
        
        purpose (str): The specific purpose of this verification (opt-in/opt-out/etc),
                     which may affect how the verification is processed and recorded.
        
        status (str): Current status of the verification code (pending/verified/expired),
                    which prevents codes from being used multiple times or after expiration.
    """
    __tablename__ = "verification_codes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    """
    Unique identifier for the verification code record using UUID format stored as string.
    UUIDs prevent ID collisions and support distributed systems and data migrations.
    """
    
    user_id = Column(String, ForeignKey("contacts.id"), nullable=False)
    """
    Reference to the contact this verification code was issued to. This is required
    to link the verification process to a specific individual and their contact record.
    """
    
    code = Column(String, nullable=False)
    """
    The actual verification code value. This is required and should be a secure,
    randomly generated value of sufficient complexity to prevent guessing.
    """
    
    channel = Column(String, nullable=True)  # Optional, derived from contact_type
    """
    The communication channel used to send the code. This is nullable as it can be
    derived from the contact type, but storing it explicitly provides a clearer
    audit trail.
    """
    
    sent_to = Column(String, nullable=True)  # Optional, for tracking purposes only
    """
    The original recipient contact information. This is nullable and may be stored
    in masked form for audit purposes while protecting the actual contact details.
    """
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    """
    When the code will expire. This is required for security reasons, as verification
    codes should have a limited validity period to reduce the risk of unauthorized use.
    """
    
    verified_at = Column(DateTime(timezone=True), nullable=True)
    """
    Timestamp when the code was successfully verified. This is nullable as it's only
    populated after successful verification, providing an audit trail of when
    verification occurred.
    """
    
    purpose = Column(String, nullable=False)
    """
    The specific purpose of this verification. This is required to ensure that the
    verification is processed correctly according to its intended use case.
    """
    
    status = Column(String, default=VerificationStatusEnum.pending.value)
    """
    Current status of the verification code. Defaults to 'pending' when created
    and is updated to 'verified' or 'expired' as appropriate. This prevents codes
    from being used multiple times or after expiration.
    """
