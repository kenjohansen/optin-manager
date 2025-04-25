"""
crud/user.py

CRUD operations for the Contact model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.user import Contact, ContactTypeEnum
from app.schemas.user import ContactCreate, ContactUpdate
import logging
from app.core.encryption import encrypt_pii, decrypt_pii, generate_deterministic_id, mask_email, mask_phone

logger = logging.getLogger(__name__)

def get_contact(db: Session, contact_id: str):
    """
    Retrieve a contact by their ID.
    Args:
        db (Session): SQLAlchemy database session.
        contact_id (str): Contact unique identifier (deterministic ID).
    Returns:
        Contact: Contact object if found, else None.
    """
    return db.query(Contact).filter(Contact.id == contact_id).first()

def get_contact_by_value(db: Session, contact_value: str, contact_type: str = None):
    """
    Retrieve a contact by their email or phone value.
    Args:
        db (Session): SQLAlchemy database session.
        contact_value (str): Email or phone value.
        contact_type (str, optional): Type of contact ('email' or 'phone').
            If not provided, it will be inferred from the value.
    Returns:
        Contact: Contact object if found, else None.
    """
    # Determine contact type if not provided
    if not contact_type:
        contact_type = "email" if "@" in contact_value else "phone"
    
    # Generate deterministic ID to look up the contact
    contact_id = generate_deterministic_id(contact_value)
    logger.info(f"Looking up contact with deterministic ID: {contact_id}")
    
    return db.query(Contact).filter(Contact.id == contact_id).first()

def create_contact(db: Session, contact: ContactCreate):
    """
    Create a new contact record with encrypted data.
    Args:
        db (Session): SQLAlchemy database session.
        contact (ContactCreate): Contact creation data.
    Returns:
        Contact: Created contact object.
    """
    # Extract contact value and type
    contact_value = contact.contact_value
    contact_type = contact.contact_type
    
    # Generate deterministic ID and encrypt the contact value
    contact_id = generate_deterministic_id(contact_value)
    encrypted_value = encrypt_pii(contact_value)
    
    logger.info(f"Creating contact with ID: {contact_id}, type: {contact_type}")
    
    # Create contact object with encrypted data
    db_contact = Contact(
        id=contact_id,
        encrypted_value=encrypted_value,
        contact_type=contact_type,
        status=contact.status,
        is_admin=contact.is_admin,
        is_staff=contact.is_staff,
        comment=contact.comment
    )
    
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
    # Update only the allowed fields
    update_data = contact_update.model_dump(exclude_unset=True)
    
    # Note: We don't allow updating the contact value or type as that would change the ID
    for key, value in update_data.items():
        if key not in ['contact_value', 'contact_type']:
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
    """
    Return paginated contacts for admin listing with masked values.
    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
    Returns:
        list: List of Contact objects.
    """
    return db.query(Contact).offset(skip).limit(limit).all()

def get_masked_contact_value(contact):
    """
    Get a masked version of the contact value for display purposes.
    Args:
        contact (Contact): Contact object.
    Returns:
        str: Masked contact value.
    """
    try:
        # Decrypt the contact value
        decrypted_value = decrypt_pii(contact.encrypted_value)
        
        # Apply appropriate masking based on contact type
        if contact.contact_type == ContactTypeEnum.email.value:
            return mask_email(decrypted_value)
        else:
            return mask_phone(decrypted_value)
    except Exception as e:
        logger.error(f"Error masking contact value: {str(e)}")
        return "[Encrypted]"
