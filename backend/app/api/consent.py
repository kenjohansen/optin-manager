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
    
    This endpoint enables the creation of explicit consent records tied to specific opt-in programs.
    Maintaining separate consent records is essential for regulatory compliance (GDPR, CCPA, etc.)
    and provides an audit trail of when and how users provided their consent.
    
    Args:
        consent (ConsentCreate): Consent creation data including contact ID and opt-in ID.
        db (Session): SQLAlchemy database session.
        
    Returns:
        ConsentOut: Created consent object with generated ID and timestamps.
    """
    db_consent = crud_consent.create_consent(db, consent)
    return db_consent

@router.get("/{consent_id}", response_model=ConsentOut)
def read_consent(consent_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a consent record by its ID.
    
    This endpoint allows retrieving detailed information about a specific consent record,
    which is necessary for auditing purposes and to verify the consent status of a particular
    contact for a specific opt-in program. This supports compliance requirements to demonstrate
    proof of consent when requested.
    
    Args:
        consent_id (str): Consent unique identifier.
        db (Session): SQLAlchemy database session.
        
    Returns:
        ConsentOut: Consent object if found, containing all consent details including timestamps.
        
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
    
    This endpoint allows modifying an existing consent record, which is necessary when
    users change their consent preferences. Updating rather than creating new records
    maintains the historical relationship between the contact and opt-in program while
    recording the change in consent status. This supports the user's right to withdraw
    or modify consent as required by privacy regulations.
    
    Args:
        consent_id (str): Consent unique identifier.
        consent_update (ConsentUpdate): Update data including new consent status.
        db (Session): SQLAlchemy database session.
        
    Returns:
        ConsentOut: Updated consent object with refreshed timestamps.
        
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
    
    This endpoint provides the ability to completely remove a consent record from the system.
    While updating consent status is generally preferred for audit purposes, deletion may be
    necessary in specific scenarios such as honoring a user's "right to be forgotten" request
    under GDPR or similar privacy regulations, or when correcting erroneously created records.
    
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
