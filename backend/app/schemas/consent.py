"""
schemas/consent.py

Pydantic schemas for the Consent entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union
from datetime import datetime
import uuid

class ConsentBase(BaseModel):
    """
    Shared fields for Consent schemas.
    
    The Consent schema is the cornerstone of the OptIn Manager system, as it represents
    the explicit permission given by a user to receive specific types of communications.
    This schema captures all the essential elements required for regulatory compliance
    with privacy laws like GDPR and CCPA, including who gave consent, what they consented
    to, when consent was given or revoked, and how it was verified.
    
    Attributes:
        user_id (str): User unique identifier, linking consent to a specific contact.
                     This relationship is critical for user-centric consent management
                     and for honoring individual privacy preferences.
        
        optin_id (str, optional): OptIn program unique identifier, specifying what
                                 the user has consented to. This can be nullable to
                                 support global opt-out scenarios.
        
        channel (str): Communication channel this consent applies to (email/SMS).
                      Different channels may have different regulatory requirements
                      and user preferences.
        
        status (str, optional): Consent status (pending/opt-in/opt-out), the core
                              indicator of whether communications are permitted.
        
        consent_timestamp (str, optional): When consent was given, critical for
                                         compliance audit trails and expiration tracking.
        
        revoked_timestamp (str, optional): When consent was revoked, if applicable,
                                         essential for compliance documentation.
        
        verification_id (uuid.UUID, optional): Reference to the verification code used
                                             to confirm consent, providing proof of verification.
        
        record (str, optional): Encrypted JSON record containing additional consent
                              metadata such as IP address and user agent.
        
        notes (str, optional): Freeform notes provided by the contact during the
                             consent process, capturing additional context.
    """
    user_id: str
    optin_id: Optional[str] = None
    channel: str
    status: Optional[str] = "pending"
    consent_timestamp: Optional[str] = None
    revoked_timestamp: Optional[str] = None
    verification_id: Optional[uuid.UUID] = None
    record: Optional[str] = None
    notes: Optional[str] = None
    notes: Optional[str] = None

class ConsentCreate(ConsentBase):
    """
    Schema for creating a new consent record.
    
    This schema inherits all fields from ConsentBase without adding additional
    requirements. Creating explicit consent records is essential for regulatory
    compliance and provides an audit trail of when and how users provided their
    consent. The schema ensures all necessary consent data is captured at creation time.
    """
    pass

class ConsentUpdate(BaseModel):
    """
    Schema for updating an existing consent record.
    
    This schema makes all fields optional, allowing partial updates to consent records.
    This is particularly important for recording consent status changes (opt-in/opt-out)
    without modifying other consent attributes. The ability to update specific fields
    like status or add revocation timestamps is critical for maintaining an accurate
    history of consent changes as required by privacy regulations.
    """
    user_id: Optional[str] = None  # Updated user reference if needed
    optin_id: Optional[str] = None  # Updated opt-in program reference if needed
    channel: Optional[str] = None  # Updated channel if needed
    status: Optional[str] = None  # Updated consent status (most common update)
    consent_timestamp: Optional[str] = None  # Updated consent timestamp if needed
    revoked_timestamp: Optional[str] = None  # When consent was withdrawn
    verification_id: Optional[str] = None  # Updated verification reference if needed
    record: Optional[str] = None  # Updated metadata if needed
    notes: Optional[str] = None  # Updated notes if provided by user

class ConsentOut(ConsentBase):
    """
    Schema for returning consent records via API.
    
    This schema extends ConsentBase to include system-generated fields like ID and
    timestamps that are essential for client applications and audit purposes. The
    inclusion of both the consent-specific timestamps (consent_timestamp, revoked_timestamp)
    and system timestamps (created_at, updated_at) provides a complete audit trail
    of both the user's consent actions and when those records were created or modified
    in the system.
    
    Attributes:
        id (str): Consent unique identifier, necessary for referencing specific
                consent records in API operations and frontend displays.
        
        created_at (Union[datetime, str], optional): System timestamp when the consent
                                                   record was created, important for
                                                   internal auditing.
        
        updated_at (Union[datetime, str], optional): System timestamp when the consent
                                                   record was last modified, important
                                                   for tracking record changes.
    """
    id: str  # Unique identifier for this specific consent record
    created_at: Optional[Union[datetime, str]] = None  # When the record was created in the system
    updated_at: Optional[Union[datetime, str]] = None  # When the record was last modified
    model_config = ConfigDict(from_attributes=True)  # Enable ORM model -> Pydantic conversion
