"""
api/contact.py

Contact API endpoints for the OptIn Manager backend.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.contact import ContactCreate, ContactUpdate, ContactOut
from app.crud import contact as crud_contact
from app.core.database import get_db
from app.core.encryption import generate_deterministic_id, mask_email, mask_phone, decrypt_pii
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

from app.schemas.contact import ContactListResponse

@router.get("/", response_model=ContactListResponse)
def list_contacts(
    search: Optional[str] = None,
    consent: Optional[str] = None,
    time_window: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_db)
):
    """Return filtered list of contacts with masked values.
    
    Args:
        search: Email or phone to search for
        consent: Filter by consent status ('opted_in' or 'opted_out')
        time_window: Filter by contacts updated in the last N days
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    logger.info(f"Listing contacts with filters: search={search}, consent={consent}, time_window={time_window}")
    
    # Get contacts with filters
    contacts = crud_contact.list_contacts_with_filters(
        db, 
        search=search, 
        consent=consent, 
        time_window=time_window,
        skip=skip, 
        limit=limit
    )
    
    logger.info(f"Found {len(contacts)} contacts matching filters")
    
    # Add masked values to each contact and format for frontend
    result = []
    for contact in contacts:
        # Get the masked value
        masked_value = crud_contact.get_masked_contact_value(contact)
        
        # Get the decrypted value (for internal use only)
        decrypted_value = None
        try:
            decrypted_value = decrypt_pii(contact.encrypted_value)
        except Exception as e:
            logger.error(f"Error decrypting contact value: {str(e)}")
        
        # Get consent status for this contact
        from app.models.consent import Consent, ConsentStatusEnum
        consent_record = db.query(Consent).filter(Consent.user_id == contact.id).order_by(Consent.consent_timestamp.desc()).first()
        consent_status = 'Unknown'
        if consent_record:
            if consent_record.status == ConsentStatusEnum.opt_in.value:
                consent_status = 'Opted In'
            elif consent_record.status == ConsentStatusEnum.opt_out.value:
                consent_status = 'Opted Out'
            else:
                consent_status = 'Pending'
        
        # Format the contact for frontend with all required fields from ContactOut schema
        contact_dict = {
            "id": contact.id,
            "masked_value": masked_value,
            "contact_type": contact.contact_type,
            "status": contact.status,
            "is_admin": contact.is_admin,
            "is_staff": contact.is_staff,
            "created_at": contact.created_at,
            "updated_at": contact.updated_at,
            "comment": contact.comment,
            "consent": consent_status,
            "last_updated": contact.updated_at,  # This is used by the frontend but not in schema
            "email": None,
            "phone": None
        }
        
        # Add email or phone field based on contact type
        if contact.contact_type == 'email' and decrypted_value:
            contact_dict["email"] = decrypted_value
        elif contact.contact_type == 'phone' and decrypted_value:
            contact_dict["phone"] = decrypted_value
        
        result.append(contact_dict)
    
    logger.info(f"Returning {len(result)} contacts to frontend")
    return {"contacts": result}

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
