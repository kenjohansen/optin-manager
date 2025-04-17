"""
schemas/user.py

Pydantic schemas for the User entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
import uuid

class ContactBase(BaseModel):
    """
    Shared fields for Contact schemas.
    Attributes:
        email (Optional[EmailStr]): Contact email address.
        phone (Optional[str]): Contact phone number.
        status (Optional[str]): Contact status (active/inactive).
    """
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = "active"

class ContactCreate(ContactBase):
    """Schema for creating a new contact record."""
    pass

class ContactUpdate(ContactBase):
    """Schema for updating an existing contact record."""
    pass

class ContactOut(ContactBase):
    """
    Schema for returning contact records via API.
    Attributes:
        id (uuid.UUID): Contact unique identifier.
    """
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
