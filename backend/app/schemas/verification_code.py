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
    Attributes:
        user_id (str): User unique identifier.
        code (str): Verification code value.
        channel (str): Channel used (sms/email).
        sent_to (str): Recipient contact (phone/email).
        expires_at (datetime): Expiration timestamp.
        verified_at (Optional[datetime]): When code was verified.
        purpose (str): Purpose of verification (opt-in/opt-out/etc).
        status (Optional[str]): Verification status.
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
    """Schema for creating a new verification code record."""
    pass

class VerificationCodeUpdate(BaseModel):
    """Schema for updating an existing verification code record."""
    user_id: Optional[str] = None
    code: Optional[str] = None
    channel: Optional[str] = None
    sent_to: Optional[str] = None
    expires_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    purpose: Optional[str] = None
    status: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class VerificationCodeOut(VerificationCodeBase):
    """
    Schema for returning verification code records via API.
    Attributes:
        id (str): Verification code unique identifier.
    """
    id: str
