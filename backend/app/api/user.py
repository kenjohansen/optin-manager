"""
api/user.py

User API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import ContactCreate, ContactUpdate, ContactOut
from app.crud import user as crud_contact
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/", response_model=ContactOut)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """
    Create a new contact.
    Args:
        contact (ContactCreate): Contact creation data.
        db (Session): SQLAlchemy database session.
    Returns:
        ContactOut: Created contact object.
    """
    db_contact = crud_contact.create_contact(db, contact)
    return db_contact

@router.get("/{contact_id}", response_model=ContactOut)
def read_contact(contact_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a contact by their ID.
    Args:
        contact_id (uuid.UUID): Contact unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        ContactOut: Contact object if found.
    Raises:
        HTTPException: 404 if contact not found.
    """
    db_contact = crud_contact.get_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user by their ID.
    Args:
        user_id (uuid.UUID): User unique identifier.
        user_update (UserUpdate): Update data.
        db (Session): SQLAlchemy database session.
    Returns:
        UserOut: Updated user object.
    Raises:
        HTTPException: 404 if user not found.
    """
    db_user = crud_user.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_user.update_user(db, db_user, user_update)

@router.delete("/{user_id}")
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a user by their ID.
    Args:
        user_id (uuid.UUID): User unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        dict: {"ok": True} on successful deletion.
    Raises:
        HTTPException: 404 if user not found.
    """
    db_user = crud_user.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    crud_user.delete_user(db, db_user)
    return {"ok": True}
