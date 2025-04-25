"""
crud/consent.py

CRUD operations for the Consent model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.consent import Consent
from app.schemas.consent import ConsentCreate, ConsentUpdate
import uuid

def get_consent(db: Session, consent_id):
    """
    Retrieve a consent record by its ID.
    Args:
        db (Session): SQLAlchemy database session.
        consent_id: Consent unique identifier (string or UUID).
    Returns:
        Consent: Consent object if found, else None.
    """
    # Handle both string and UUID inputs for backward compatibility
    if isinstance(consent_id, uuid.UUID):
        consent_id = str(consent_id)
    elif isinstance(consent_id, str) and '-' not in consent_id and len(consent_id) == 32:
        # Handle non-hyphenated UUIDs by converting to hyphenated format
        consent_id = str(uuid.UUID(consent_id))
    
    return db.query(Consent).filter(Consent.id == consent_id).first()

def create_consent(db: Session, consent: ConsentCreate):
    """
    Create a new consent record.
    Args:
        db (Session): SQLAlchemy database session.
        consent (ConsentCreate): Consent creation data.
    Returns:
        Consent: Created consent object.
    """
    db_consent = Consent(**consent.model_dump())
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent

def update_consent(db: Session, db_consent: Consent, consent_update: ConsentUpdate):
    """
    Update an existing consent record.
    Args:
        db (Session): SQLAlchemy database session.
        db_consent (Consent): Consent object to update.
        consent_update (ConsentUpdate): Update data.
    Returns:
        Consent: Updated consent object.
    """
    for key, value in consent_update.model_dump(exclude_unset=True).items():
        setattr(db_consent, key, value)
    db.commit()
    db.refresh(db_consent)
    return db_consent

def delete_consent(db: Session, db_consent: Consent):
    """
    Delete a consent record.
    Args:
        db (Session): SQLAlchemy database session.
        db_consent (Consent): Consent object to delete.
    Returns:
        None
    """
    db.delete(db_consent)
    db.commit()
