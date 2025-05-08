"""
models/message_template.py

SQLAlchemy model for the MessageTemplate entity in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class MessageTemplateChannelEnum(str, Enum):
    """
    Enumeration for message template channels.
    
    Different communication channels have different format requirements, character
    limitations, and regulatory considerations. Templates must be designed specifically
    for each channel to ensure optimal delivery and compliance with channel-specific
    regulations (e.g., SMS character limits or email formatting requirements).
    """
    sms = "sms"     # Short Message Service (text messages)
    email = "email" # Email communications

class MessageTemplate(Base):
    """
    SQLAlchemy model for message template records.
    
    Message templates are essential for ensuring consistent, compliant communications
    across the system. Using templates rather than ad-hoc messages helps maintain
    consistency, reduces the risk of errors, and simplifies the process of sending
    messages to contacts.
    
    Templates can include placeholders for personalization, making communications
    more relevant to recipients while still adhering to approved messaging guidelines.
    This is particularly important for regulatory compliance, where specific language
    or disclosures may be required in certain types of communications.
    
    The template system allows administrators to create and manage standard message
    formats that can be reused across multiple communications, ensuring that all
    messages follow approved guidelines and contain necessary legal language.
    
    Attributes:
        id (UUID): Unique identifier for the template. Using UUID format ensures
                 global uniqueness and supports distributed systems.
        
        name (str): Descriptive name for the template that helps administrators
                  quickly identify and select the appropriate template for
                  different communication needs.
        
        content (str): The actual template content, which may include placeholders
                     for dynamic content. Templates ensure consistent messaging
                     and compliance with communication standards.
        
        channel (str): The communication channel this template is designed for
                     (sms/email). Different channels have different format
                     requirements and character limitations.
                     
        description (str): Additional context about the template's purpose and
                        usage, helping administrators understand when and how
                        to use each template.
        
        created_at (datetime): When the template was created, useful for
                            auditing and version tracking.
    """
    __tablename__ = "message_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    """
    Unique identifier for the template using native UUID format. Using UUIDs
    prevents ID collisions and supports distributed systems and data migrations.
    """
    
    name = Column(String, nullable=False)
    """
    Descriptive name for the template. This is required as it helps administrators
    quickly identify and select the appropriate template in the UI.
    """
    
    content = Column(String, nullable=False)
    """
    The actual template content, which may include placeholders for dynamic content.
    This is required as it forms the basis of all communications generated from
    this template.
    """
    
    channel = Column(String, nullable=False)
    """
    The communication channel this template is designed for (sms/email). This is
    required as different channels have different format requirements and character
    limitations that affect template design.
    """
    
    description = Column(String, nullable=True)
    """
    Additional context about the template's purpose and usage. This is optional
    but recommended to help administrators understand when and how to use each
    template.
    """
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    """
    Timestamp when the template was created. This is automatically set by the
    database and is useful for auditing and version tracking.
    """
