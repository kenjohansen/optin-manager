"""
schemas/message_template.py

Pydantic schemas for the MessageTemplate entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class MessageTemplateBase(BaseModel):
    """
    Shared fields for MessageTemplate schemas.
    Attributes:
        name (str): Template name.
        content (str): Template content.
        channel (str): Communication channel (sms/email).
        description (Optional[str]): Template description.
    """
    name: str
    content: str
    channel: str
    description: Optional[str] = None

class MessageTemplateCreate(MessageTemplateBase):
    """Schema for creating a new message template record."""
    pass

class MessageTemplateUpdate(MessageTemplateBase):
    """Schema for updating an existing message template record."""
    pass

class MessageTemplateOut(MessageTemplateBase):
    """
    Schema for returning message template records via API.
    Attributes:
        id (uuid.UUID): Template unique identifier.
        created_at (Optional[str]): Creation timestamp.
    """
    id: uuid.UUID
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
