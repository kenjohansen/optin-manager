"""
crud/message_template.py

CRUD operations for the MessageTemplate model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.message_template import MessageTemplate
from app.schemas.message_template import MessageTemplateCreate, MessageTemplateUpdate
import uuid

def get_message_template(db: Session, template_id: uuid.UUID):
    """
    Retrieve a message template by its ID.
    
    This function allows administrators to access specific message templates for
    viewing, editing, or using as the basis for communications. Templates are
    essential for ensuring consistent, compliant communications across the system,
    and being able to retrieve them by ID is necessary for the template management
    interface.
    
    Args:
        db (Session): SQLAlchemy database session.
        template_id (uuid.UUID): MessageTemplate unique identifier.
        
    Returns:
        MessageTemplate: MessageTemplate object if found, else None.
    """
    return db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()

def create_message_template(db: Session, template: MessageTemplateCreate):
    """
    Create a new message template record.
    
    This function enables administrators to define standard message formats that
    can be reused across multiple communications. Using templates rather than
    ad-hoc messages helps maintain consistency, reduces the risk of errors, and
    simplifies the process of sending messages to contacts.
    
    Templates are particularly important for regulatory compliance, where specific
    language or disclosures may be required in certain types of communications.
    By creating and managing templates centrally, the system ensures that all
    messages follow approved guidelines and contain necessary legal language.
    
    Args:
        db (Session): SQLAlchemy database session.
        template (MessageTemplateCreate): MessageTemplate creation data including
                                        name, content, channel, and description.
        
    Returns:
        MessageTemplate: Created message template object with generated ID.
    """
    db_template = MessageTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def update_message_template(db: Session, db_template: MessageTemplate, template_update: MessageTemplateUpdate):
    """
    Update an existing message template record.
    
    This function allows administrators to modify existing templates when legal
    requirements change, branding is updated, or communication strategies evolve.
    The ability to update templates centrally ensures that all future communications
    immediately reflect these changes, maintaining compliance and consistency.
    
    Template updates might be necessary for various reasons:
    - Regulatory changes requiring updated disclosures or language
    - Branding updates that affect messaging tone or visual elements
    - Improvements to message clarity or effectiveness based on feedback
    - Correction of errors or inaccuracies in existing templates
    
    Args:
        db (Session): SQLAlchemy database session.
        db_template (MessageTemplate): Existing template object to update.
        template_update (MessageTemplateUpdate): Update data with modified fields.
        
    Returns:
        MessageTemplate: Updated message template object with new content.
    """
    for key, value in template_update.model_dump(exclude_unset=True).items():
        setattr(db_template, key, value)
    db.commit()
    db.refresh(db_template)
    return db_template

def delete_message_template(db: Session, db_template: MessageTemplate):
    """
    Delete a message template record.
    
    This function should be used with caution, especially if the template has been
    used to generate messages. While deleting unused or obsolete templates helps
    keep the template library manageable, it's important to consider whether the
    template might be referenced by existing message records.
    
    In many cases, it's preferable to archive or disable templates rather than
    deleting them, especially if they've been used for communications that might
    need to be audited or reviewed in the future. This function is primarily
    provided for removing templates that were created in error or that are truly
    no longer needed.
    
    Args:
        db (Session): SQLAlchemy database session.
        db_template (MessageTemplate): MessageTemplate object to delete.
        
    Returns:
        None
    """
    db.delete(db_template)
    db.commit()
