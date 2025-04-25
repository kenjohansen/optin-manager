"""
api/contact.py

Contact API endpoints for the OptIn Manager backend.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.user import ContactCreate, ContactUpdate, ContactOut
from app.crud import user as crud_contact
from app.core.database import get_db
from app.core.encryption import generate_deterministic_id, mask_email, mask_phone
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/", response_model=ContactOut)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    # Check if contact already exists
    existing_contact = crud_contact.get_contact_by_value(db, contact.contact_value, contact.contact_type)
    if existing_contact:
        logger.info(f"Contact already exists with ID: {existing_contact.id}")
        # Return existing contact with masked value
        masked_value = crud_contact.get_masked_contact_value(existing_contact)
        return {
            **existing_contact.__dict__,
            "masked_value": masked_value
        }
    
    # Create new contact
    db_contact = crud_contact.create_contact(db, contact)
    
    # Return with masked value
    masked_value = crud_contact.get_masked_contact_value(db_contact)
    return {
        **db_contact.__dict__,
        "masked_value": masked_value
    }

@router.get("/", response_model=List[ContactOut])
def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return paginated list of contacts with masked values."""
    contacts = crud_contact.list_contacts(db, skip=skip, limit=limit)
    
    # Add masked values to each contact
    result = []
    for contact in contacts:
        masked_value = crud_contact.get_masked_contact_value(contact)
        result.append({
            **contact.__dict__,
            "masked_value": masked_value
        })
    
    return result

@router.get("/{contact_id}", response_model=ContactOut)
def read_contact(contact_id: str, db: Session = Depends(get_db)):
    db_contact = crud_contact.get_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Return with masked value
    masked_value = crud_contact.get_masked_contact_value(db_contact)
    return {
        **db_contact.__dict__,
        "masked_value": masked_value
    }

@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: str, contact_update: ContactUpdate, db: Session = Depends(get_db)):
    db_contact = crud_contact.get_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    updated_contact = crud_contact.update_contact(db, db_contact, contact_update)
    
    # Return with masked value
    masked_value = crud_contact.get_masked_contact_value(updated_contact)
    return {
        **updated_contact.__dict__,
        "masked_value": masked_value
    }

@router.delete("/{contact_id}")
def delete_contact(contact_id: str, db: Session = Depends(get_db)):
    db_contact = crud_contact.get_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    crud_contact.delete_contact(db, db_contact)
    return {"ok": True}

@router.get("/lookup/by-value", response_model=ContactOut)
def lookup_contact_by_value(
    value: str = Query(..., description="Email or phone value to look up"),
    contact_type: Optional[str] = Query(None, description="Type of contact (email/phone)")
):
    """Look up a contact by their email or phone value."""
    # Generate deterministic ID for the contact value
    contact_id = generate_deterministic_id(value)
    
    # Return a response with the ID and masked value
    # This endpoint doesn't actually query the database, it just generates the ID
    # that would be used to look up the contact
    
    # Determine contact type if not provided
    if not contact_type:
        contact_type = "email" if "@" in value else "phone"
    
    # Apply appropriate masking
    if contact_type == "email":
        masked_value = mask_email(value)
    else:
        masked_value = mask_phone(value)
    
    return {
        "id": contact_id,
        "masked_value": masked_value,
        "contact_type": contact_type
    }
