"""
schemas/message.py

Pydantic schemas for the Message entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid

class MessageBase(BaseModel):
    """
    Shared fields for Message schemas.
    Attributes:
        user_id (uuid.UUID): User unique identifier.
        campaign_id (Optional[uuid.UUID]): Campaign unique identifier.
        template_id (Optional[uuid.UUID]): Message template unique identifier.
        channel (str): Message channel (sms/email).
        content (str): Message content.
        status (Optional[str]): Message status.
        sent_at (Optional[str]): When message was sent.
        delivery_status (Optional[str]): Delivery status JSON string.
    """
    user_id: uuid.UUID
    campaign_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    channel: str
    content: str
    status: Optional[str] = "pending"
    sent_at: Optional[str] = None
    delivery_status: Optional[str] = None

class MessageCreate(MessageBase):
    """Schema for creating a new message record."""
    pass

class MessageUpdate(MessageBase):
    """Schema for updating an existing message record."""
    pass

class MessageOut(MessageBase):
    """
    Schema for returning message records via API.
    Attributes:
        id (uuid.UUID): Message unique identifier.
        opt_in_status (str): Opt-in status for the recipient (pending/opt-in/opt-out).
        delivery_status (Optional[str]): Delivery status JSON string.
        timeline (Optional[list]): Timeline of message/opt-in events.
    """
    id: uuid.UUID
    opt_in_status: str
    delivery_status: Optional[str] = None
    timeline: Optional[list] = None
    model_config = ConfigDict(from_attributes=True)
