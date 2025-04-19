"""
schemas/campaign.py

Pydantic schemas for the Campaign entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum

class CampaignStatusEnum(str, Enum):
    """Enumeration for campaign status values."""
    active = "active"
    paused = "paused"
    archived = "archived"
    closed = "closed"

class CampaignBase(BaseModel):
    """
    Shared fields for Campaign schemas.
    Attributes:
        name (str): Name of the campaign.
        type (Optional[str]): Campaign type (transactional/promotional).
        status (Optional[str]): Campaign status (active/paused/archived/closed).
    """
    name: str
    type: Optional[str] = "transactional"
    status: Optional[CampaignStatusEnum] = CampaignStatusEnum.active

class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign record."""
    pass

class CampaignUpdate(CampaignBase):
    """Schema for updating an existing campaign record."""
    pass

class CampaignOut(CampaignBase):
    """
    Schema for returning campaign records via API.
    Attributes:
        id (uuid.UUID): Campaign unique identifier.
        created_at (Optional[str]): Creation timestamp.
    """
    id: uuid.UUID
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
