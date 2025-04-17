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
    Args:
        db (Session): SQLAlchemy database session.
        template (MessageTemplateCreate): MessageTemplate creation data.
    Returns:
        MessageTemplate: Created message template object.
    """
    db_template = MessageTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def update_message_template(db: Session, db_template: MessageTemplate, template_update: MessageTemplateUpdate):
    """
    Update an existing message template record.
    Args:
        db (Session): SQLAlchemy database session.
        db_template (MessageTemplate): MessageTemplate object to update.
        template_update (MessageTemplateUpdate): Update data.
    Returns:
        MessageTemplate: Updated message template object.
    """
    for key, value in template_update.model_dump(exclude_unset=True).items():
        setattr(db_template, key, value)
    db.commit()
    db.refresh(db_template)
    return db_template

def delete_message_template(db: Session, db_template: MessageTemplate):
    """
    Delete a message template record.
    Args:
        db (Session): SQLAlchemy database session.
        db_template (MessageTemplate): MessageTemplate object to delete.
    Returns:
        None
    """
    db.delete(db_template)
    db.commit()
