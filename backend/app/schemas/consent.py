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
    Attributes:
        user_id (uuid.UUID): User unique identifier.
        optin_id (uuid.UUID): OptIn unique identifier.
        channel (str): Consent channel (sms/email).
        status (Optional[str]): Consent status.
        consent_timestamp (Optional[str]): Timestamp when consent was given.
        revoked_timestamp (Optional[str]): Timestamp when consent was revoked.
        verification_id (Optional[uuid.UUID]): Verification code reference.
        record (Optional[str]): Encrypted JSON record.
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
    """Schema for creating a new consent record."""
    pass

class ConsentUpdate(BaseModel):
    """Schema for updating an existing consent record."""
    user_id: Optional[str] = None
    optin_id: Optional[str] = None
    channel: Optional[str] = None
    status: Optional[str] = None
    consent_timestamp: Optional[str] = None
    revoked_timestamp: Optional[str] = None
    verification_id: Optional[str] = None
    record: Optional[str] = None
    notes: Optional[str] = None

class ConsentOut(ConsentBase):
    """
    Schema for returning consent records via API.
    Attributes:
        id (str): Consent unique identifier.
        created_at (Union[datetime, str]): Creation timestamp.
    """
    id: str
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    model_config = ConfigDict(from_attributes=True)
