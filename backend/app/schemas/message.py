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
    
    The Message schema represents communications sent to contacts through various
    channels. This is a critical component for tracking all communications sent
    through the system, which is essential for compliance with privacy regulations
    and for providing an audit trail of all contact interactions.
    
    Each message is linked to both a specific contact and an opt-in program,
    ensuring that communications are properly categorized and can be traced back
    to the consent that authorized them. This linkage is crucial for demonstrating
    compliance with consent requirements.
    
    Attributes:
        user_id (str): User unique identifier linking this message to a specific
                     contact. This relationship is essential for tracking which
                     contact received the message and for compliance reporting.
        
        optin_id (str): OptIn program unique identifier linking this message to
                      a specific opt-in program. This relationship establishes
                      that the message was sent under the authorization of a
                      specific consent program.
        
        template_id (Optional[uuid.UUID]): Message template unique identifier,
                                         if the message was generated from a
                                         template. Templates ensure consistency
                                         in communications and compliance with
                                         approved messaging.
        
        channel (str): Communication channel used (sms/email), determining how
                     the message was delivered. Different channels have different
                     regulatory requirements and delivery characteristics.
        
        content (str): Actual message content sent to the recipient. Storing the
                     exact content is essential for compliance and audit purposes,
                     showing exactly what was communicated.
        
        status (Optional[str]): Current message status (pending/sent/failed),
                              tracking the lifecycle of the message delivery process.
        
        sent_at (Optional[str]): When the message was sent, critical for timing
                               compliance and for troubleshooting delivery issues.
        
        delivery_status (Optional[str]): Detailed delivery status information as
                                       a JSON string, providing technical details
                                       about the delivery process and outcome.
    """
    user_id: str
    optin_id: str
    template_id: Optional[uuid.UUID] = None
    channel: str
    content: str
    status: Optional[str] = "pending"
    sent_at: Optional[str] = None
    delivery_status: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class MessageCreate(MessageBase):
    """
    Schema for creating a new message record.
    
    This schema inherits all fields from MessageBase without adding additional
    requirements. Creating message records is essential for maintaining a complete
    audit trail of all communications sent through the system, which is a key
    requirement for compliance with privacy regulations.
    
    Messages are typically created automatically by the system when sending
    communications, rather than being created manually by users. This ensures
    that all communications are properly recorded and tracked.
    """
    pass

class MessageUpdate(BaseModel):
    """
    Schema for updating an existing message record.
    
    This schema makes all fields optional, allowing partial updates to message records.
    The most common updates are to the status field (to reflect delivery status changes)
    and the delivery_status field (to record detailed delivery information received
    from the communication provider).
    
    While most fields should generally not be changed after creation (like the content
    or recipient), the schema allows for these updates in exceptional cases, such as
    correcting errors in the message record. Maintaining accurate message records is
    critical for compliance and audit purposes.
    """
    user_id: Optional[str] = None  # Updated user reference if needed (rare)
    optin_id: Optional[str] = None  # Updated opt-in reference if needed (rare)
    template_id: Optional[uuid.UUID] = None  # Updated template reference if needed (rare)
    channel: Optional[str] = None  # Updated channel if needed (rare)
    content: Optional[str] = None  # Updated content if needed (rare)
    status: Optional[str] = None  # Updated status (common update)
    sent_at: Optional[str] = None  # Updated sent timestamp if needed
    delivery_status: Optional[str] = None  # Updated delivery status (common update)
    
    model_config = ConfigDict(from_attributes=True)

class MessageOut(MessageBase):
    """
    Schema for returning message records via API.
    
    This schema extends MessageBase to include system-generated fields like ID
    and additional context information like the recipient's opt-in status. This
    additional context is valuable for administrative interfaces that display
    message history, as it provides a complete picture of the communication
    context without requiring additional queries.
    
    The inclusion of opt_in_status is particularly important for compliance
    monitoring, as it allows administrators to verify that messages were only
    sent to contacts with appropriate consent status at the time of sending.
    
    Attributes:
        id (str): Message unique identifier, necessary for referencing specific
                message records in API operations and for tracking individual
                communications.
        
        opt_in_status (str): Opt-in status for the recipient at the time the
                           message was sent (pending/opt-in/opt-out). This provides
                           critical context for compliance verification.
        
        delivery_status (Optional[str]): Detailed delivery status information
                                       as a JSON string, providing technical details
                                       about the delivery process and outcome.
    """
    id: str  # Unique identifier for this specific message record
    opt_in_status: Optional[str] = None  # Recipient's consent status when message was sent
    delivery_status: Optional[str] = None  # Detailed delivery status information
    model_config = ConfigDict(from_attributes=True)
