"""
schemas/optin.py

Pydantic schemas for the OptIn entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum

class OptInTypeEnum(str, Enum):
    """
    Enumeration of opt-in program types for categorizing different communication purposes.
    
    These categories are essential for regulatory compliance as different jurisdictions
    have different requirements for different types of communications. For example,
    promotional communications typically require explicit opt-in, while transactional
    communications may be sent without explicit consent in some cases.
    """
    promotional = "promotional"  # Marketing and promotional communications
    transactional = "transactional"  # Essential service communications like receipts
    alert = "alert"  # Time-sensitive notifications and alerts

class OptInStatusEnum(str, Enum):
    """
    Enumeration of opt-in program statuses to track lifecycle states.
    
    These statuses allow administrators to control the operational state of opt-in
    programs without deleting data, which is important for maintaining audit trails
    and compliance records while still being able to temporarily or permanently
    disable specific communication programs.
    """
    active = "active"  # Program is currently active and accepting new consents
    paused = "paused"  # Program is temporarily inactive but may be resumed
    archived = "archived"  # Program is no longer in use but retained for historical records
    closed = "closed"  # Program is permanently discontinued

class OptInBase(BaseModel):
    """
    Base schema for opt-in program data with common fields used across create/update operations.
    
    This base class defines the core attributes that all opt-in programs must have,
    ensuring consistency across the system. The default values for type and status
    provide sensible starting points that align with common regulatory requirements
    while allowing customization when needed.
    """
    name: str  # Human-readable name for the opt-in program
    type: OptInTypeEnum = OptInTypeEnum.transactional  # Default to transactional as it's generally less restrictive
    description: Optional[str] = None  # Detailed description of what the program covers
    status: OptInStatusEnum = OptInStatusEnum.active  # Default to active state for immediate use

class OptInCreate(OptInBase):
    """
    Schema for creating a new opt-in program.
    
    This schema inherits all fields from OptInBase without adding additional
    requirements, as the base fields provide all necessary information to create
    a valid opt-in program. This approach ensures that all required fields are
    properly validated during the creation process.
    """
    pass

class OptInUpdate(BaseModel):
    """
    Schema for updating an existing opt-in program.
    
    This schema makes all fields optional, allowing partial updates to opt-in programs.
    This is important for administrative flexibility, as it enables changing individual
    attributes (like status) without needing to provide all other fields. This pattern
    supports PATCH-style API operations and reduces the risk of unintentional changes.
    """
    name: Optional[str] = None  # Updated name if changing
    type: Optional[OptInTypeEnum] = None  # Updated type if changing
    description: Optional[str] = None  # Updated description if changing
    status: Optional[OptInStatusEnum] = None  # Updated status if changing

class OptInOut(OptInBase):
    """
    Schema for returning opt-in program data via API responses.
    
    This schema extends OptInBase to include system-generated fields like ID and
    timestamps that are essential for client applications to track and reference
    specific opt-in programs. The model_config setting enables automatic conversion
    from ORM models to this Pydantic schema, simplifying API response generation.
    
    The inclusion of timestamps is particularly important for compliance and audit
    purposes, as it allows tracking when opt-in programs were created and modified.
    """
    id: uuid.UUID  # Unique identifier for referencing this specific opt-in program
    created_at: Optional[datetime] = None  # When the opt-in program was created
    updated_at: Optional[datetime] = None  # When the opt-in program was last modified
    model_config = ConfigDict(from_attributes=True)  # Enable ORM model -> Pydantic conversion
