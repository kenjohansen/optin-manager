"""
api/consent.py

Consent API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.consent import ConsentCreate, ConsentUpdate, ConsentOut
from app.crud import consent as crud_consent
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/consents", tags=["consents"])

@router.post("/", response_model=ConsentOut)
def create_consent(consent: ConsentCreate, db: Session = Depends(get_db)):
    """
    Create a new consent record.
    Args:
        consent (ConsentCreate): Consent creation data.
        db (Session): SQLAlchemy database session.
    Returns:
        ConsentOut: Created consent object.
    """
    db_consent = crud_consent.create_consent(db, consent)
    return db_consent

@router.get("/{consent_id}", response_model=ConsentOut)
def read_consent(consent_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a consent record by its ID.
    Args:
        consent_id (str): Consent unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        ConsentOut: Consent object if found.
    Raises:
        HTTPException: 404 if consent not found.
    """
    db_consent = crud_consent.get_consent(db, consent_id)
    if not db_consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    return db_consent

@router.put("/{consent_id}", response_model=ConsentOut)
def update_consent(consent_id: str, consent_update: ConsentUpdate, db: Session = Depends(get_db)):
    """
    Update a consent record by its ID.
    Args:
        consent_id (uuid.UUID): Consent unique identifier.
        consent_update (ConsentUpdate): Update data.
        db (Session): SQLAlchemy database session.
    Returns:
        ConsentOut: Updated consent object.
    Raises:
        HTTPException: 404 if consent not found.
    """
    db_consent = crud_consent.get_consent(db, consent_id)
    if not db_consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    return crud_consent.update_consent(db, db_consent, consent_update)

@router.delete("/{consent_id}", response_model=dict)
def delete_consent(consent_id: str, db: Session = Depends(get_db)):
    """
    Delete a consent record by its ID.
    Args:
        consent_id (str): Consent unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        dict: {"ok": True} on successful deletion.
    Raises:
        HTTPException: 404 if consent not found.
    """
    db_consent = crud_consent.get_consent(db, consent_id)
    if not db_consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    crud_consent.delete_consent(db, db_consent)
    return {"ok": True}
