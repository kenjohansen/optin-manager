"""
api/message_template.py

MessageTemplate API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.message_template import MessageTemplateCreate, MessageTemplateUpdate, MessageTemplateOut
from app.crud import message_template as crud_template
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/message-templates", tags=["message_templates"])

@router.post("/", response_model=MessageTemplateOut)
def create_message_template(template: MessageTemplateCreate, db: Session = Depends(get_db)):
    """
    Create a new message template.
    Args:
        template (MessageTemplateCreate): Template creation data.
        db (Session): SQLAlchemy database session.
    Returns:
        MessageTemplateOut: Created message template object.
    """
    db_template = crud_template.create_message_template(db, template)
    return db_template

@router.get("/{template_id}", response_model=MessageTemplateOut)
def read_message_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a message template by its ID.
    Args:
        template_id (uuid.UUID): Template unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        MessageTemplateOut: Message template object if found.
    Raises:
        HTTPException: 404 if message template not found.
    """
    db_template = crud_template.get_message_template(db, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Message template not found")
    return db_template

@router.put("/{template_id}", response_model=MessageTemplateOut)
def update_message_template(template_id: uuid.UUID, template_update: MessageTemplateUpdate, db: Session = Depends(get_db)):
    """
    Update a message template by its ID.
    Args:
        template_id (uuid.UUID): Template unique identifier.
        template_update (MessageTemplateUpdate): Update data.
        db (Session): SQLAlchemy database session.
    Returns:
        MessageTemplateOut: Updated message template object.
    Raises:
        HTTPException: 404 if message template not found.
    """
    db_template = crud_template.get_message_template(db, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Message template not found")
    return crud_template.update_message_template(db, db_template, template_update)

@router.delete("/{template_id}")
def delete_message_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a message template by its ID.
    Args:
        template_id (uuid.UUID): Template unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        dict: {"ok": True} on successful deletion.
    Raises:
        HTTPException: 404 if message template not found.
    """
    db_template = crud_template.get_message_template(db, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Message template not found")
    crud_template.delete_message_template(db, db_template)
    return {"ok": True}
