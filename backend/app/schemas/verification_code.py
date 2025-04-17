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
        user_id (uuid.UUID): User unique identifier.
        code (str): Verification code value.
        channel (str): Channel used (sms/email).
        sent_to (str): Recipient contact (phone/email).
        expires_at (str): Expiration timestamp.
        verified_at (Optional[str]): When code was verified.
        purpose (str): Purpose of verification (opt-in/opt-out/etc).
        status (Optional[str]): Verification status.
    """
    user_id: uuid.UUID
    code: str
    channel: str
    sent_to: str
    expires_at: datetime
    verified_at: Optional[datetime] = None
    purpose: str
    status: Optional[str] = "pending"

class VerificationCodeCreate(VerificationCodeBase):
    """Schema for creating a new verification code record."""
    pass

class VerificationCodeUpdate(VerificationCodeBase):
    """Schema for updating an existing verification code record."""
    pass

class VerificationCodeOut(VerificationCodeBase):
    """
    Schema for returning verification code records via API.
    Attributes:
        id (uuid.UUID): Verification code unique identifier.
    """
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
