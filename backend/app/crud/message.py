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

def get_message(db: Session, message_id: uuid.UUID):
    """
    Retrieve a message by its ID.
    Args:
        db (Session): SQLAlchemy database session.
        message_id (uuid.UUID): Message unique identifier.
    Returns:
        Message: Message object if found, else None.
    """
    return db.query(Message).filter(Message.id == message_id).first()

def create_message(db: Session, message: MessageCreate):
    """
    Create a new message record.
    Args:
        db (Session): SQLAlchemy database session.
        message (MessageCreate): Message creation data.
    Returns:
        Message: Created message object.
    """
    db_message = Message(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message(db: Session, db_message: Message, message_update: MessageUpdate):
    """
    Update an existing message record.
    Args:
        db (Session): SQLAlchemy database session.
        db_message (Message): Message object to update.
        message_update (MessageUpdate): Update data.
    Returns:
        Message: Updated message object.
    """
    for key, value in message_update.model_dump(exclude_unset=True).items():
        setattr(db_message, key, value)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, db_message: Message):
    """
    Delete a message record.
    Args:
        db (Session): SQLAlchemy database session.
        db_message (Message): Message object to delete.
    Returns:
        None
    """
    db.delete(db_message)
    db.commit()
