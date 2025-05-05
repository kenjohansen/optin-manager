"""
schemas/contact.py

Pydantic schemas for the Contact entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from typing import Optional, Literal, Union
from datetime import datetime
from enum import Enum
from app.models.contact import ContactTypeEnum

class ContactBase(BaseModel):
    """
    Shared fields for Contact schemas.
    Attributes:
        contact_value (str): Contact value (email or phone).
        contact_type (str): Type of contact (email/phone).
        status (Optional[str]): Contact status (active/inactive).
    """
    contact_value: str
    contact_type: Literal["email", "phone"]
    status: Optional[str] = "active"
    
    @field_validator('contact_value')
    def validate_contact_value(cls, v, info):
        values = info.data
        if 'contact_type' in values:
            if values['contact_type'] == 'email' and '@' not in v:
                raise ValueError('Invalid email format')
            elif values['contact_type'] == 'phone' and not any(c.isdigit() for c in v):
                raise ValueError('Phone number must contain digits')
        return v

class ContactCreate(ContactBase):
    """Schema for creating a new contact record."""
    is_admin: Optional[bool] = False
    is_staff: Optional[bool] = False
    comment: Optional[str] = None

class ContactUpdate(BaseModel):
    """Schema for updating an existing contact record."""
    status: Optional[str] = None
    is_admin: Optional[bool] = None
    is_staff: Optional[bool] = None
    comment: Optional[str] = None

class ContactOut(BaseModel):
    """
    Schema for returning contact records via API.
    Attributes:
        id (str): Contact unique identifier (deterministic ID).
        masked_value (str): Masked contact value for display.
        contact_type (str): Type of contact (email/phone).
        status (str): Contact status.
        is_admin (bool): Whether the contact has admin privileges.
        is_staff (bool): Whether the contact has staff privileges.
        consent (str): Consent status (Opted In/Opted Out).
        email (str): Email address (will be masked in API responses).
        phone (str): Phone number (will be masked in API responses).
    """
    id: str
    masked_value: str
    contact_type: str
    status: str
    is_admin: bool = False
    is_staff: bool = False
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    comment: Optional[str] = None
    consent: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ContactListResponse(BaseModel):
    """
    Schema for returning a list of contacts with pagination metadata.
    Attributes:
        contacts (List[ContactOut]): List of contact records.
    """
    contacts: list[ContactOut]
