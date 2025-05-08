"""
models/optin.py

SQLAlchemy model for the OptIn entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func
# Use String type for UUID in SQLite
from sqlalchemy import String as UUID
import uuid
from app.core.database import Base
import enum

class OptInTypeEnum(str, enum.Enum):
    """
    Enumeration of opt-in program types to categorize different communication purposes.
    
    These categories are essential for regulatory compliance as different jurisdictions
    have different requirements for different types of communications. For example,
    promotional communications typically require explicit opt-in, while transactional
    communications may be sent without explicit consent in some cases.
    """
    promotional = "promotional"  # Marketing and promotional communications
    transactional = "transactional"  # Essential service communications like receipts
    alert = "alert"  # Time-sensitive notifications and alerts

class OptInStatusEnum(str, enum.Enum):
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

class OptIn(Base):
    """
    SQLAlchemy model representing an opt-in program in the system.
    
    The OptIn model is the central entity for managing communication consent programs.
    Each opt-in program represents a specific type of communication that users can
    consent to receive. Separating communications into distinct opt-in programs
    allows for granular consent management, which is essential for compliance with
    privacy regulations like GDPR and CCPA that require specific, unbundled consent.
    """
    __tablename__ = "optins"
    
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    """
    Unique identifier for the opt-in program using UUID format stored as string.
    UUIDs are used to prevent ID collisions in distributed systems and potential
    future data migrations or merges.
    """
    
    name = Column(String, nullable=False)
    """
    Human-readable name for the opt-in program displayed in the admin interface.
    This is required for administrators to easily identify different programs.
    """
    
    type = Column(Enum(OptInTypeEnum), default=OptInTypeEnum.transactional, nullable=False)
    """
    Type of communication this opt-in program represents (promotional, transactional, alert).
    This categorization is essential for applying the appropriate regulatory requirements
    and business rules to different types of communications.
    """
    
    description = Column(String, nullable=True)
    """
    Detailed description of the opt-in program's purpose and the types of communications
    it covers. This helps administrators understand the program's scope and may be
    displayed to users when obtaining consent.
    """
    
    status = Column(Enum(OptInStatusEnum), default=OptInStatusEnum.active, nullable=False)
    """
    Current operational status of the opt-in program (active, paused, archived, closed).
    This allows administrators to control program availability without deleting data,
    which is important for maintaining audit trails and compliance records.
    """
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    """
    Timestamp when the opt-in program was created, automatically set by the database.
    This is important for audit trails and understanding the program's lifecycle.
    """
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    """
    Timestamp when the opt-in program was last updated, automatically updated by the database.
    This helps track changes to the program configuration over time for compliance purposes.
    """
