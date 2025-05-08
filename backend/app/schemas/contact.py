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
    
    The Contact schema represents individuals who may provide consent for communications.
    This schema is designed to securely handle personally identifiable information (PII)
    while still allowing the system to manage consent effectively. The separation of
    contact_value and contact_type enables proper validation and handling of different
    contact methods while maintaining a consistent data structure.
    
    Attributes:
        contact_value (str): Contact value (email or phone) that will be encrypted
                           before storage. This field contains sensitive PII that
                           must be protected according to privacy regulations.
        
        contact_type (str): Type of contact (email/phone), determining how the
                          system validates, encrypts, and communicates with the contact.
                          Different contact types have different regulatory requirements
                          and formatting standards.
        
        status (Optional[str]): Contact status (active/inactive), controlling whether
                              the contact should receive communications independent of
                              specific consent status. This allows for global suppression
                              when needed.
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
    """
    Schema for creating a new contact record.
    
    This schema extends ContactBase with additional fields that are only relevant
    during creation. The is_admin and is_staff fields are legacy fields maintained
    for backward compatibility but are not actively used in the current system
    architecture, which separates contacts from authenticated users.
    
    The comment field provides a way to capture additional context during contact
    creation, particularly useful for opt-out scenarios where understanding the
    reason for opt-out is valuable for improving services.
    """
    is_admin: Optional[bool] = False  # Legacy field, defaults to False for new contacts
    is_staff: Optional[bool] = False  # Legacy field, defaults to False for new contacts
    comment: Optional[str] = None  # Optional comment, often used for opt-out reasons

class ContactUpdate(BaseModel):
    """
    Schema for updating an existing contact record.
    
    This schema makes all fields optional, allowing partial updates to contact records.
    Notably, it does not include contact_value or contact_type, as these are immutable
    properties of a contact that should not be changed after creation. This design
    decision prevents accidental modification of the core identifying information
    while still allowing updates to status and other attributes.
    
    The most common update is to the status field (to mark a contact as inactive)
    or to the comment field (to add notes about opt-out reasons or other context).
    """
    status: Optional[str] = None  # Updated status if changing (active/inactive)
    is_admin: Optional[bool] = None  # Legacy field, rarely updated
    is_staff: Optional[bool] = None  # Legacy field, rarely updated
    comment: Optional[str] = None  # Updated comment, often used for opt-out reasons

class ContactOut(BaseModel):
    """
    Schema for returning contact records via API.
    
    This schema is designed to provide all necessary contact information to the
    frontend while protecting PII. The use of masked_value instead of the raw
    contact_value is critical for privacy protection in user interfaces and logs.
    
    The schema includes both system fields (id, status, timestamps) and derived
    fields (masked_value, consent) that are computed during API response generation.
    The email and phone fields are conditionally populated based on contact_type
    and are always masked to protect privacy.
    
    Attributes:
        id (str): Contact unique identifier (deterministic ID) generated from the
                contact value, enabling lookups without decrypting PII.
        
        masked_value (str): Masked contact value for display that preserves some
                          recognizability while protecting privacy (e.g., j***@e***.com).
        
        contact_type (str): Type of contact (email/phone), determining how the
                          masked value is formatted and how communications are sent.
        
        status (str): Contact status (active/inactive), controlling whether the
                    contact should receive communications.
        
        is_admin (bool): Legacy field indicating whether the contact has admin privileges.
        
        is_staff (bool): Legacy field indicating whether the contact has staff privileges.
        
        consent (str, optional): Derived field showing the overall consent status
                               (Opted In/Opted Out) based on related consent records.
        
        email (str, optional): Email address if contact_type is 'email', always masked
                             for privacy in API responses.
        
        phone (str, optional): Phone number if contact_type is 'phone', always masked
                             for privacy in API responses.
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
    
    This wrapper schema encapsulates a list of contact records for API responses.
    It's designed to support pagination and filtering in the contacts listing API,
    which is essential for performance when dealing with potentially large numbers
    of contacts. The structure allows for future expansion to include pagination
    metadata (total count, page number, etc.) without breaking API compatibility.
    
    Attributes:
        contacts (List[ContactOut]): List of contact records with masked values
                                   and other necessary information for display.
    """
    contacts: list[ContactOut]  # The list of contact records to return
