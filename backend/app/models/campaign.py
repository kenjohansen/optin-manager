"""
models/campaign.py

SQLAlchemy model for the Campaign entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class CampaignTypeEnum(str, Enum):
    """Enumeration for campaign types."""
    transactional = "transactional"
    promotional = "promotional"

class CampaignStatusEnum(str, Enum):
    """Enumeration for campaign status values."""
    active = "active"
    paused = "paused"
    archived = "archived"
    closed = "closed"  # New status for closed campaigns

class Campaign(Base):
    """
    SQLAlchemy model for campaign records.
    Attributes:
        id (UUID): Primary key.
        name (str): Name of the campaign.
        type (str): Campaign type (transactional/promotional).
        created_at (datetime): Creation timestamp.
        status (str): Status of the campaign. Can be 'active', 'paused', 'archived', or 'closed'.
    """
    __tablename__ = "campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, default=CampaignTypeEnum.transactional)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default=CampaignStatusEnum.active)
