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
    promotional = "promotional"
    transactional = "transactional"
    alert = "alert"

class OptInStatusEnum(str, Enum):
    active = "active"
    paused = "paused"
    archived = "archived"
    closed = "closed"

class OptInBase(BaseModel):
    name: str
    type: OptInTypeEnum = OptInTypeEnum.transactional
    description: Optional[str] = None
    status: OptInStatusEnum = OptInStatusEnum.active

class OptInCreate(OptInBase):
    pass

class OptInUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[OptInTypeEnum] = None
    description: Optional[str] = None
    status: Optional[OptInStatusEnum] = None

class OptInOut(OptInBase):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
