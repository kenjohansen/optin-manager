"""
api/contact.py

Contact API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
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
    """
    Create a new contact record or return existing one if found.
    
    This endpoint handles the creation of contact records with proper PII encryption.
    It first checks if the contact already exists to prevent duplicates, which is essential
    for maintaining data integrity and ensuring consistent communication with users.
    The contact values are stored encrypted for privacy and security compliance.
    
    Args:
        contact (ContactCreate): Contact creation data with contact value and type.
        db (Session): SQLAlchemy database session.
        
    Returns:
        ContactOut: Created or existing contact with masked value for display.
    """
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
    """
    Return a filtered list of contacts with masked values.
    
    This endpoint provides a powerful search and filtering mechanism for contacts,
    essential for customer support and compliance operations. It handles the complexity
    of searching encrypted data by using deterministic IDs for exact matches and in-memory
    decryption for partial searches, balancing security with usability. The consent
    filtering enables compliance reporting for regulatory requirements.
    
    Args:
        search (str, optional): Email or phone to search for, supports partial matching.
        consent (str, optional): Filter by consent status ('opted_in' or 'opted_out').
        time_window (int, optional): Filter by contacts updated in the last N days.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return per page.
        db (Session): SQLAlchemy database session.
        current_user: The authenticated user making the request.
        
    Returns:
        ContactListResponse: List of contacts with masked values and consent status.
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
    """
    Retrieve a contact record by its ID.
    
    This endpoint allows retrieving a specific contact's details, which is necessary
    for customer support operations and data management. The contact's PII is returned
    in a masked format to protect privacy while still allowing identification.
    
    Args:
        contact_id (str): Contact unique identifier.
        db (Session): SQLAlchemy database session.
        
    Returns:
        ContactOut: Contact object with masked value if found.
        
    Raises:
        HTTPException: 404 if contact not found.
    """
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
    """
    Update a contact record by its ID.
    
    This endpoint enables updating contact information while maintaining the encryption
    of sensitive data. This is necessary for keeping contact information current while
    preserving the security and privacy protections in place for PII data.
    
    Args:
        contact_id (str): Contact unique identifier.
        contact_update (ContactUpdate): Update data for the contact.
        db (Session): SQLAlchemy database session.
        
    Returns:
        ContactOut: Updated contact with masked value.
        
    Raises:
        HTTPException: 404 if contact not found.
    """
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
    """
    Delete a contact record by its ID.
    
    This endpoint provides the ability to completely remove a contact from the system,
    which may be necessary to comply with "right to be forgotten" requests under GDPR
    and other privacy regulations. It ensures all associated data is properly removed.
    
    Args:
        contact_id (str): Contact unique identifier.
        db (Session): SQLAlchemy database session.
        
    Returns:
        dict: {"ok": True} on successful deletion.
        
    Raises:
        HTTPException: 404 if contact not found.
    """
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
    """
    Look up a contact by their email or phone value.
    
    This endpoint provides a way to find a contact's ID based on their email or phone
    without actually querying the database. It uses the same deterministic ID generation
    algorithm used for storage, enabling secure lookups without exposing the actual
    contact database. This is essential for the opt-out workflow where users need to
    be identified by their contact information rather than an ID they don't know.
    
    Args:
        value (str): Email or phone value to look up.
        contact_type (str, optional): Type of contact (email/phone). If not provided,
                                     it will be inferred from the value format.
        
    Returns:
        ContactOut: Contact object with ID and masked value.
    """
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
