"""
crud/user.py

CRUD operations for the Contact model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.user import Contact
from app.schemas.user import ContactCreate, ContactUpdate
import uuid

def get_contact(db: Session, contact_id: uuid.UUID):
    """
    Retrieve a contact by their ID.
    Args:
        db (Session): SQLAlchemy database session.
        contact_id (uuid.UUID): Contact unique identifier.
    Returns:
        Contact: Contact object if found, else None.
    """
    return db.query(Contact).filter(Contact.id == contact_id).first()

def get_contact_by_email(db: Session, email: str):
    """
    Retrieve a contact by their email address.
    Args:
        db (Session): SQLAlchemy database session.
        email (str): Email address of the contact.
    Returns:
        Contact: Contact object if found, else None.
    """
    return db.query(Contact).filter(Contact.email == email).first()

def create_contact(db: Session, contact: ContactCreate):
    """
    Create a new contact record.
    Args:
        db (Session): SQLAlchemy database session.
        contact (ContactCreate): Contact creation data.
    Returns:
        Contact: Created contact object.
    """
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, db_contact: Contact, contact_update: ContactUpdate):
    """
    Update an existing contact record.
    Args:
        db (Session): SQLAlchemy database session.
        db_contact (Contact): Contact object to update.
        contact_update (ContactUpdate): Update data.
    Returns:
        Contact: Updated contact object.
    """
    for key, value in contact_update.model_dump(exclude_unset=True).items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, db_contact: Contact):
    """
    Delete a contact record.
    Args:
        db (Session): SQLAlchemy database session.
        db_contact (Contact): Contact object to delete.
    Returns:
        None
    """
    db.delete(db_contact)
    db.commit()

def list_contacts(db: Session, skip=0, limit=100):
    """Return paginated contacts for admin listing."""
    return db.query(Contact).offset(skip).limit(limit).all()
