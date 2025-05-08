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
    
    This function is essential for accessing specific consent records, which is
    necessary for verifying consent status, responding to user inquiries, and
    demonstrating compliance with privacy regulations. Being able to retrieve
    individual consent records by ID allows the system to check whether a user
    has consented to specific types of communications before sending messages.
    
    The flexible ID handling supports both string and UUID formats for backward
    compatibility, ensuring that consent records can be retrieved regardless of
    how they were stored or referenced.
    
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
    
    This function is the cornerstone of the OptIn Manager system, recording explicit
    user consent for specific communication types. Creating accurate consent records
    is essential for compliance with privacy regulations like GDPR and CCPA, which
    require organizations to maintain proof of consent.
    
    The consent record includes critical information such as:
    - Who provided the consent (user_id)
    - What they consented to (optin_id)
    - Which channel they consented for (email/SMS)
    - When consent was provided (consent_timestamp)
    - How consent was verified (verification_id)
    
    This comprehensive record forms the legal basis for sending communications
    and serves as evidence of compliance in case of regulatory inquiries or audits.
    
    Args:
        db (Session): SQLAlchemy database session.
        consent (ConsentCreate): Consent creation data including user ID, opt-in ID,
                               channel, status, and verification details.
        
    Returns:
        Consent: Created consent object with tracking metadata.
    """
    db_consent = Consent(**consent.model_dump())
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent

def update_consent(db: Session, db_consent: Consent, consent_update: ConsentUpdate):
    """
    Update an existing consent record.
    
    This function is critical for maintaining the complete consent lifecycle, from
    initial opt-in to potential opt-out. It allows the system to update consent
    status when users change their preferences, ensuring that their current consent
    choices are accurately reflected in the system.
    
    The most common update is changing the status from 'opt-in' to 'opt-out' when
    a user withdraws consent, which must be recorded with a revocation timestamp
    for compliance purposes. This function ensures that all consent changes are
    properly documented, maintaining a complete audit trail of user preferences
    over time.
    
    As noted in the memories, the Opt-Out workflow requires sending a verification
    code, verifying that code, and then allowing the user to manage their preferences.
    This function handles the final step of updating their consent records based on
    those preference changes.
    
    Args:
        db (Session): SQLAlchemy database session.
        db_consent (Consent): Existing consent object to update.
        consent_update (ConsentUpdate): Update data, typically status changes
                                      and revocation timestamps.
        
    Returns:
        Consent: Updated consent object with new status information.
    """
    for key, value in consent_update.model_dump(exclude_unset=True).items():
        setattr(db_consent, key, value)
    db.commit()
    db.refresh(db_consent)
    return db_consent

def delete_consent(db: Session, db_consent: Consent):
    """
    Delete a consent record.
    
    This function should be used with extreme caution, as deleting consent records
    can impact the organization's ability to demonstrate compliance with privacy
    regulations. In most cases, it's preferable to update the consent status to
    'opt-out' rather than deleting the record entirely, as this preserves the
    audit trail while still respecting the user's choice to withdraw consent.
    
    However, this function may be necessary in specific circumstances:
    - Responding to data deletion requests under GDPR's "right to be forgotten"
    - Correcting erroneously created consent records
    - Implementing data retention policies after the required retention period
    
    Before deleting any consent record, ensure that you have considered the
    regulatory implications and have documented the reason for deletion.
    
    Args:
        db (Session): SQLAlchemy database session.
        db_consent (Consent): Consent object to delete.
        
    Returns:
        None
    """
    db.delete(db_consent)
    db.commit()
