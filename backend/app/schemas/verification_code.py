"""
schemas/verification_code.py

Pydantic schemas for the VerificationCode entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class VerificationCodeBase(BaseModel):
    """
    Shared fields for VerificationCode schemas.
    
    The VerificationCode schema is a critical component of the consent verification
    process, which is essential for regulatory compliance. It provides a secure way
    to confirm that the person providing or withdrawing consent is actually the owner
    of the contact information. This verification step creates an audit trail that
    demonstrates the system took reasonable steps to verify identity before processing
    consent changes.
    
    Attributes:
        user_id (str): User unique identifier linking this verification to a specific
                     contact. This relationship is essential for tracking which contact
                     the verification applies to and for associating the verification
                     with consent records.
        
        code (str): The actual verification code value sent to the user. This is
                  typically a short, random string that is difficult to guess but
                  easy for users to enter. The code is the proof of possession of
                  the contact method.
        
        channel (str): The communication channel used for verification (sms/email).
                     Different channels may have different security considerations
                     and regulatory requirements for verification.
        
        sent_to (str): The specific recipient contact (phone/email) where the code
                     was sent. This creates an audit trail of exactly where verification
                     codes were sent, which is important for troubleshooting and compliance.
        
        expires_at (datetime): When the verification code expires, enforcing a time
                             limit on verification attempts. This security measure
                             prevents old verification codes from being used if they
                             are somehow compromised.
        
        verified_at (Optional[datetime]): When the code was successfully verified by
                                        the user, if applicable. This timestamp is
                                        critical for the audit trail of when verification
                                        actually occurred.
        
        purpose (str): The specific purpose of the verification (opt-in/opt-out/etc),
                     which determines what actions are allowed after successful verification.
                     This ensures that verification for one purpose cannot be reused for
                     another purpose.
        
        status (Optional[str]): Current verification status (pending/verified/expired).
                              This tracks the lifecycle of the verification process and
                              determines whether the code is still valid for use.
    """
    user_id: str
    code: str
    channel: str
    sent_to: str
    expires_at: datetime
    verified_at: Optional[datetime] = None
    purpose: str
    status: Optional[str] = "pending"
    
    model_config = ConfigDict(from_attributes=True)

class VerificationCodeCreate(VerificationCodeBase):
    """
    Schema for creating a new verification code record.
    
    This schema inherits all fields from VerificationCodeBase without adding additional
    requirements. Creating verification codes is a critical step in the consent workflow,
    as it initiates the process of verifying a user's identity before allowing them to
    provide or withdraw consent. The system generates these codes automatically when
    a user requests to manage their consent preferences.
    
    The creation of a verification code record also serves as an audit trail of when
    verification was attempted, even if the code is never actually verified by the user.
    """
    pass

class VerificationCodeUpdate(BaseModel):
    """
    Schema for updating an existing verification code record.
    
    This schema makes all fields optional, allowing partial updates to verification
    code records. The most common update is to the status field (to mark a code as
    verified or expired) and the verified_at timestamp (to record when verification
    occurred). The ability to update these specific fields without modifying other
    attributes is essential for maintaining an accurate record of the verification
    process.
    
    While most fields should generally not be changed after creation (like the code
    itself or the sent_to address), the schema allows for these updates in exceptional
    cases, such as correcting errors or extending expiration times.
    """
    user_id: Optional[str] = None  # Updated user reference if needed
    code: Optional[str] = None  # Updated code if needed (rare)
    channel: Optional[str] = None  # Updated channel if needed (rare)
    sent_to: Optional[str] = None  # Updated recipient if needed (rare)
    expires_at: Optional[datetime] = None  # Updated expiration if extending
    verified_at: Optional[datetime] = None  # When verification occurred (common update)
    purpose: Optional[str] = None  # Updated purpose if needed (rare)
    status: Optional[str] = None  # Updated status (common update)
    
    model_config = ConfigDict(from_attributes=True)

class VerificationCodeOut(VerificationCodeBase):
    """
    Schema for returning verification code records via API.
    
    This schema extends VerificationCodeBase to include the system-generated ID
    that uniquely identifies each verification code record. The ID is essential
    for API operations that reference specific verification codes, such as when
    verifying a code or checking its status.
    
    When returning verification codes via the API, the system typically masks or
    omits the actual code value for security reasons, especially after verification
    has occurred. This prevents the code from being reused or intercepted.
    
    Attributes:
        id (str): Verification code unique identifier, necessary for referencing
                specific verification records in API operations and for associating
                verification with consent records.
    """
    id: str  # Unique identifier for this specific verification code record
