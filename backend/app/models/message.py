"""
models/message.py

SQLAlchemy model for the Message entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class MessageStatusEnum(str, Enum):
    """
    Enumeration for message status values.
    
    Tracking the status of each message is critical for regulatory compliance
    and auditing purposes. These statuses allow the system to maintain a complete
    record of all communication attempts and their outcomes, which may be required
    for legal or compliance reviews.
    """
    pending = "pending"     # Message is queued but not yet sent
    sent = "sent"         # Message has been sent to the provider
    delivered = "delivered" # Provider confirmed delivery to recipient
    failed = "failed"      # Message failed to send or deliver

class MessageChannelEnum(str, Enum):
    """
    Enumeration for message channels.
    
    Different communication channels have different regulatory requirements
    and consent management needs. Tracking the channel used for each message
    ensures that communications comply with channel-specific regulations
    (e.g., SMS regulations like TCPA in the US or email regulations like CAN-SPAM).
    """
    sms = "sms"     # Short Message Service (text messages)
    email = "email" # Email communications

class Message(Base):
    """
    SQLAlchemy model for message records.
    
    The Message model is a critical component for regulatory compliance and auditing.
    It maintains a complete record of all communications sent through the system,
    including the content, recipient, related opt-in program, delivery status, and
    timestamps. This comprehensive record is essential for demonstrating compliance
    with regulations like GDPR, CCPA, TCPA, and CAN-SPAM, which require organizations
    to maintain records of consent and communications.
    
    The model stores the actual message content in encrypted form to protect
    potentially sensitive information, while still maintaining a complete audit trail.
    This approach balances security requirements with compliance needs.
    
    Attributes:
        id (str): Primary key (UUID as string) that uniquely identifies each message
                for tracking and auditing purposes.
        
        user_id (str): Foreign key to the contact record, identifying who received
                     the message. This links communications to specific individuals
                     for consent tracking and opt-out management.
        
        optin_id (str): Foreign key to the opt-in program that authorized this
                      communication. This establishes the legal basis for sending
                      the message and links it to specific consent records.
        
        template_id (UUID): Foreign key to the message template used to generate
                         this message. Using templates ensures consistency and
                         compliance with approved messaging standards.
        
        channel (str): The communication channel used (sms/email), which determines
                     the applicable regulations and delivery mechanisms.
        
        content (str): The actual message content in encrypted form. Encryption
                     protects sensitive information while maintaining the audit trail.
        
        status (str): Current message status (pending/sent/delivered/failed),
                    essential for tracking delivery and troubleshooting issues.
        
        sent_at (datetime): Timestamp when the message was sent, critical for
                         compliance with time-sensitive regulations and for
                         calculating frequency limits.
        
        delivery_status (str): Detailed delivery status information from the
                            provider as a JSON string, providing additional
                            context for troubleshooting and auditing.
    """
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    """
    Unique identifier for the message record using UUID format stored as string.
    UUIDs prevent ID collisions and support distributed systems and data migrations.
    """
    
    user_id = Column(String, ForeignKey("contacts.id"), nullable=False)
    """
    Reference to the contact who received this message. This is a required field
    as every message must have a recipient for proper consent tracking.
    """
    
    optin_id = Column(String, ForeignKey("optins.id"), nullable=False)
    """
    Reference to the opt-in program that authorized this communication. This is
    required to establish the legal basis for the communication and to link the
    message to specific consent records.
    """
    
    template_id = Column(UUID(as_uuid=True), ForeignKey("message_templates.id"), nullable=True)
    """
    Reference to the message template used. This is nullable as some messages
    might be generated dynamically without using a predefined template.
    """
    
    channel = Column(String, nullable=False)
    """
    The communication channel used (sms/email). This is required as different
    channels have different regulatory requirements and delivery mechanisms.
    """
    
    content = Column(String, nullable=False)  # Encrypted
    """
    The actual message content, stored in encrypted form to protect potentially
    sensitive information while maintaining a complete audit trail.
    """
    
    status = Column(String, default=MessageStatusEnum.pending)
    """
    Current status of the message in the delivery lifecycle. Defaults to 'pending'
    when the message is first created and is updated as the message progresses.
    """
    
    sent_at = Column(DateTime(timezone=True), nullable=True)
    """
    Timestamp when the message was sent. This is nullable as it's only populated
    after the message has been successfully sent to the provider.
    """
    
    delivery_status = Column(String, nullable=True)  # JSON string
    """
    Detailed delivery status information from the provider as a JSON string.
    This provides additional context for troubleshooting and auditing.
    """
