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
    
    The MessageTemplate schema represents reusable message templates that can be
    used to generate consistent communications. Templates are essential for ensuring
    that all communications follow approved messaging guidelines and contain the
    necessary legal language and formatting.
    
    Using templates rather than ad-hoc messages helps maintain consistency in
    communications, reduces the risk of errors, and simplifies the process of
    sending messages to contacts. Templates can also include placeholders for
    personalization, making communications more relevant to recipients.
    
    Attributes:
        name (str): Template name for identification and selection in the UI.
                  A descriptive name helps administrators quickly find the
                  appropriate template for different communication needs.
        
        content (str): The actual template content, which may include placeholders
                     for dynamic content. Templates ensure consistent messaging
                     and compliance with communication standards.
        
        channel (str): The communication channel this template is designed for
                     (sms/email). Different channels have different format
                     requirements and character limitations.
        
        description (Optional[str]): Additional context about the template's
                                   purpose and usage. This helps administrators
                                   understand when and how to use each template.
    """
    name: str
    content: str
    channel: str
    description: Optional[str] = None

class MessageTemplateCreate(MessageTemplateBase):
    """
    Schema for creating a new message template record.
    
    This schema inherits all fields from MessageTemplateBase without adding additional
    requirements. Creating message templates is typically done by administrators who
    need to define standard communications for different purposes.
    
    Templates are created once and then reused many times, which improves efficiency
    and ensures consistency across all communications of a similar type. This is
    particularly important for regulatory compliance, where specific language or
    disclosures may be required in certain types of communications.
    """
    pass

class MessageTemplateUpdate(MessageTemplateBase):
    """
    Schema for updating an existing message template record.
    
    This schema inherits all fields from MessageTemplateBase, requiring all fields
    to be provided even for updates. This approach ensures that template updates
    are complete and consistent, preventing partial updates that might result in
    incomplete or inconsistent templates.
    
    Template updates might be necessary when legal requirements change, branding
    is updated, or communication strategies evolve. The ability to update templates
    centrally ensures that all future communications immediately reflect these changes.
    """
    pass

class MessageTemplateOut(MessageTemplateBase):
    """
    Schema for returning message template records via API.
    
    This schema extends MessageTemplateBase to include system-generated fields like
    ID and creation timestamp. These additional fields are important for template
    management interfaces, allowing administrators to track when templates were
    created and to reference specific templates by their unique identifiers.
    
    The creation timestamp is particularly useful for auditing purposes, as it
    allows administrators to understand which version of a template was in use
    at a particular point in time, which may be relevant for compliance reviews.
    
    Attributes:
        id (uuid.UUID): Template unique identifier, necessary for referencing
                      specific templates in API operations and for associating
                      messages with the templates they were generated from.
        
        created_at (Optional[datetime]): When the template was created, useful
                                       for auditing and version tracking.
    """
    id: uuid.UUID  # Unique identifier for this specific template
    created_at: Optional[datetime] = None  # When the template was created
    model_config = ConfigDict(from_attributes=True)  # Enable ORM model -> Pydantic conversion
