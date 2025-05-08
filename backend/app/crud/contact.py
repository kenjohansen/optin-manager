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
    
    This function is essential for accessing specific contact records using their
    deterministic ID. The system uses deterministic IDs derived from the contact
    value (email/phone) to enable lookups without decrypting the data, balancing
    security with functionality.
    
    As noted in the memories, contacts are stored with encrypted values, so this
    ID-based lookup is the primary way to efficiently retrieve contact records
    without exposing the actual contact information.
    
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
    
    This function is critical for the verification process, allowing the system to
    check if a contact already exists before creating a new record. It works by
    generating the same deterministic ID that would have been used when creating
    the contact, then looking up that ID in the database.
    
    This approach allows the system to find contacts based on their email or phone
    without storing these values in plaintext, which is essential for protecting
    personally identifiable information (PII) while still maintaining functionality.
    
    As noted in the memories, the search functionality was fixed to work with
    encrypted contact values by generating deterministic IDs from search terms
    and looking for matching patterns.
    
    Args:
        db (Session): SQLAlchemy database session.
        contact_value (str): Email or phone value to look up.
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
    
    This function is fundamental to the OptIn Manager system, as it securely stores
    contact information while protecting personally identifiable information (PII).
    It implements a critical security pattern by:
    
    1. Generating a deterministic ID from the contact value, which allows lookups
       without decrypting the data
    2. Encrypting the actual contact value before storage, ensuring that PII is
       never stored in plaintext
    
    This approach balances security requirements with functional needs, allowing
    the system to manage contacts and their consent while maintaining strong
    privacy protections. This is essential for compliance with regulations like
    GDPR and CCPA that require appropriate security measures for personal data.
    
    Args:
        db (Session): SQLAlchemy database session.
        contact (ContactCreate): Contact creation data including the contact value
                               (email/phone) and type.
        
    Returns:
        Contact: Created contact object with encrypted data and deterministic ID.
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
    
    This function allows for updates to contact metadata while maintaining the
    security of the contact's PII. Importantly, it does not allow updating the
    actual contact value (email/phone) or type, as these are used to generate
    the deterministic ID that serves as the primary key.
    
    This restriction is intentional and ensures the integrity of the contact
    identification system. If a contact's email or phone changes, a new contact
    record should be created instead, preserving the history of the original
    contact for compliance and audit purposes.
    
    The function primarily allows updates to status, comment, and other metadata
    fields that don't affect the contact's identity.
    
    Args:
        db (Session): SQLAlchemy database session.
        db_contact (Contact): Existing contact object to update.
        contact_update (ContactUpdate): Update data for allowed fields only.
        
    Returns:
        Contact: Updated contact object with new metadata.
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
    
    This function should be used with extreme caution, as deleting contact records
    can impact related consent records and the organization's ability to demonstrate
    compliance with privacy regulations. In most cases, it's preferable to update
    the contact status to 'inactive' rather than deleting the record entirely.
    
    However, this function may be necessary in specific circumstances:
    - Responding to data deletion requests under GDPR's "right to be forgotten"
    - Correcting erroneously created contact records
    - Implementing data retention policies after the required retention period
    
    Before deleting any contact record, ensure that you have considered the
    regulatory implications and have documented the reason for deletion.
    
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
    
    This function supports the administrative interface for contact management,
    providing a paginated list of contacts. Pagination is essential for performance
    when dealing with large numbers of contacts, preventing memory issues and
    ensuring responsive UI.
    
    The contact values are not decrypted in the database query itself, but rather
    in memory when needed for display, and even then they are masked to protect
    privacy. This approach maintains security while still allowing administrators
    to view and manage contacts.
    
    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return per page.
        
    Returns:
        list: List of Contact objects for the requested page.
    """
    return db.query(Contact).offset(skip).limit(limit).all()

def list_contacts_with_filters(db: Session, search=None, consent=None, time_window=None, skip=0, limit=100):
    """
    Return filtered contacts based on search criteria.
    
    This function is critical for the Contacts Lookup page, allowing administrators
    to search and filter contacts based on various criteria. As noted in the memories,
    this function was updated to address several issues with the search functionality:
    
    1. For complete email searches: It generates a deterministic ID from the search
       term and looks for contacts with matching ID patterns
    2. For partial searches or phone numbers: It fetches records and decrypts them
       in memory to check for matches
    3. The consent filtering was updated to properly join with the Consent table
    4. The time window was increased from 7 to 365 days to show more historical contacts
    
    This approach balances security (by not storing plaintext contact information)
    with functionality (by enabling search capabilities), which is essential for
    a usable contact management interface that still protects PII.
    
    Args:
        db (Session): SQLAlchemy database session.
        search (str, optional): Email or phone to search for.
        consent (str, optional): Filter by consent status ('opted_in' or 'opted_out').
        time_window (int, optional): Filter by contacts updated in the last N days.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return per page.
        
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
