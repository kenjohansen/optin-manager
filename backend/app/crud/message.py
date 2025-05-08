"""
crud/message.py

CRUD operations for the Message model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate
import uuid

def get_message(db: Session, message_id: str):
    """
    Retrieve a message by its ID.
    
    This function is essential for accessing specific message records, which is
    necessary for auditing, compliance verification, and troubleshooting delivery
    issues. Being able to retrieve individual messages by ID allows administrators
    to investigate specific communications when needed.
    
    Args:
        db (Session): SQLAlchemy database session.
        message_id (str): Message unique identifier.
        
    Returns:
        Message: Message object if found, else None.
    """
    return db.query(Message).filter(Message.id == message_id).first()

def create_message(db: Session, message: MessageCreate):
    """
    Create a new message record.
    
    This function records all communications sent through the system, which is
    critical for regulatory compliance with privacy laws like GDPR, CCPA, TCPA,
    and CAN-SPAM. These records serve as an audit trail demonstrating that
    communications were sent only to users who provided appropriate consent.
    
    The message content is stored in encrypted form to protect potentially
    sensitive information while still maintaining the complete audit trail.
    This balances security requirements with compliance needs.
    
    Args:
        db (Session): SQLAlchemy database session.
        message (MessageCreate): Message creation data including user ID, opt-in ID,
                               channel, and encrypted content.
        
    Returns:
        Message: Created message object with generated ID and metadata.
    """
    db_message = Message(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message(db: Session, db_message: Message, message_update: MessageUpdate):
    """
    Update an existing message record.
    
    This function allows for updates to message records, particularly for tracking
    delivery status changes. As message providers report back on delivery status
    (sent, delivered, failed), this function updates the message record to reflect
    the current state, which is important for monitoring system performance and
    troubleshooting delivery issues.
    
    For compliance reasons, the system maintains the original message content and
    metadata while updating only the status fields, preserving the integrity of
    the audit trail.
    
    Args:
        db (Session): SQLAlchemy database session.
        db_message (Message): Existing message object to update.
        message_update (MessageUpdate): Update data, typically status and
                                      delivery information.
        
    Returns:
        Message: Updated message object with new status information.
    """
    for key, value in message_update.model_dump(exclude_unset=True).items():
        setattr(db_message, key, value)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, db_message: Message):
    """
    Delete a message record.
    
    This function should be used with caution, as deleting message records may
    impact the system's ability to demonstrate compliance with privacy regulations.
    In most cases, it's preferable to retain all message records for the required
    retention period defined by applicable regulations.
    
    This function is primarily provided for data management purposes, such as
    implementing data retention policies or responding to data deletion requests
    under privacy regulations like GDPR's "right to be forgotten."
    
    Args:
        db (Session): SQLAlchemy database session.
        db_message (Message): Message object to delete.
        
    Returns:
        None
    """
    db.delete(db_message)
    db.commit()
