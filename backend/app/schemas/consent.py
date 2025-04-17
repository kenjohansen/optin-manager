"""
schemas/consent.py

Pydantic schemas for the Consent entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid

class ConsentBase(BaseModel):
    """
    Shared fields for Consent schemas.
    Attributes:
        user_id (uuid.UUID): User unique identifier.
        campaign_id (Optional[uuid.UUID]): Campaign unique identifier.
        channel (str): Consent channel (sms/email).
        status (Optional[str]): Consent status.
        consent_timestamp (Optional[str]): Timestamp when consent was given.
        revoked_timestamp (Optional[str]): Timestamp when consent was revoked.
        verification_id (Optional[uuid.UUID]): Verification code reference.
        record (Optional[str]): Encrypted JSON record.
    """
    user_id: uuid.UUID
    campaign_id: Optional[uuid.UUID] = None
    channel: str
    status: Optional[str] = "pending"
    consent_timestamp: Optional[str] = None
    revoked_timestamp: Optional[str] = None
    verification_id: Optional[uuid.UUID] = None
    record: Optional[str] = None

class ConsentCreate(ConsentBase):
    """Schema for creating a new consent record."""
    pass

class ConsentUpdate(ConsentBase):
    """Schema for updating an existing consent record."""
    pass

class ConsentOut(ConsentBase):
    """
    Schema for returning consent records via API.
    Attributes:
        id (uuid.UUID): Consent unique identifier.
    """
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
