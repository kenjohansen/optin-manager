"""
crud/contact.py

CRUD operations for the Contact model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.contact import Contact, ContactTypeEnum
from app.schemas.contact import ContactCreate, ContactUpdate
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

def list_contacts_with_filters(db: Session, search=None, consent=None, time_window=None, skip=0, limit=100):
    """
    Return filtered contacts based on search criteria.
    Args:
        db (Session): SQLAlchemy database session.
        search (str, optional): Email or phone to search for.
        consent (str, optional): Filter by consent status ('opted_in' or 'opted_out').
        time_window (int, optional): Filter by contacts updated in the last N days.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
    Returns:
        list: List of Contact objects matching the filters.
    """
    import logging
    from datetime import datetime, timedelta
    from sqlalchemy import or_
    
    logger = logging.getLogger(__name__)
    
    # Start with a base query
    query = db.query(Contact)
    
    # Apply search filter if provided
    if search:
        logger.info(f"Applying search filter: {search}")
        # Since values are encrypted, we can't do a direct search
        # Instead, we'll generate a deterministic ID for the search term
        # and check if any contact IDs start with that pattern
        # This is an approximation and won't catch all matches
        
        # For email searches
        if '@' in search:
            # This is likely an email search
            search_id = generate_deterministic_id(search)
            logger.info(f"Searching for email with deterministic ID starting with: {search_id[:10]}")
            query = query.filter(
                Contact.id.startswith(search_id[:10])
            )
        else:
            # For phone searches or partial searches, we'll need to fetch all and filter in memory
            # This is not ideal for large datasets but works for our current needs
            logger.info("Using fallback search method for non-email or partial search")
            # We'll fetch all and filter later in Python code
            pass
    
    # Apply consent filter if provided
    if consent:
        logger.info(f"Applying consent filter: {consent}")
        # We need to join with the Consent table to filter by consent status
        from app.models.consent import Consent, ConsentStatusEnum
        
        if consent.lower() == 'opted_in':
            query = query.join(Consent, Contact.id == Consent.user_id)
            query = query.filter(Consent.status == ConsentStatusEnum.opt_in.value)
        elif consent.lower() == 'opted_out':
            query = query.join(Consent, Contact.id == Consent.user_id)
            query = query.filter(Consent.status == ConsentStatusEnum.opt_out.value)
    
    # Apply time window filter if provided
    if time_window:
        logger.info(f"Applying time window filter: {time_window} days")
        cutoff_date = datetime.utcnow() - timedelta(days=int(time_window))
        # Handle NULL updated_at values - include them in results
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Contact.updated_at >= cutoff_date,
                Contact.updated_at == None
            )
        )
        logger.info(f"Modified time window filter to include NULL updated_at values")
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Log the SQL query for debugging
    logger.info(f"SQL Query: {query}")
    
    # Execute query
    results = query.all()
    logger.info(f"Initial query returned {len(results)} results")
    
    # For non-email searches or partial searches, we need to do post-filtering
    if search and '@' not in search:
        # We need to decrypt and check each contact value
        filtered_results = []
        for contact in results:
            try:
                # Decrypt the contact value
                decrypted_value = decrypt_pii(contact.encrypted_value)
                
                # Check if the search term is in the decrypted value
                if search.lower() in decrypted_value.lower():
                    filtered_results.append(contact)
            except Exception as e:
                logger.error(f"Error decrypting contact value: {str(e)}")
        
        logger.info(f"Post-filtering reduced results from {len(results)} to {len(filtered_results)}")
        results = filtered_results
    
    logger.info(f"Found {len(results)} contacts matching filters")
    return results

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
