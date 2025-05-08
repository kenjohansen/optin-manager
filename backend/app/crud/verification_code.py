"""
crud/verification_code.py

CRUD operations for the VerificationCode model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.verification_code import VerificationCode
from app.schemas.verification_code import VerificationCodeCreate, VerificationCodeUpdate
import uuid

def get_verification_code(db: Session, code_id):
    """
    Retrieve a verification code record by its ID.
    
    This function is essential for the verification process, allowing the system
    to retrieve and validate verification codes during the opt-in/opt-out workflow.
    As noted in the memories, the Opt-Out workflow requires sending a verification
    code, verifying that code, and then allowing the user to manage their preferences.
    
    The flexible ID handling supports both string and UUID formats for backward
    compatibility, ensuring that verification codes can be retrieved regardless of
    how they were stored or referenced.
    
    Args:
        db (Session): SQLAlchemy database session.
        code_id: VerificationCode unique identifier (string or UUID).
        
    Returns:
        VerificationCode: VerificationCode object if found, else None.
    """
    # Handle both string and UUID inputs for backward compatibility
    if isinstance(code_id, uuid.UUID):
        code_id = str(code_id)
    elif isinstance(code_id, str) and '-' not in code_id and len(code_id) == 32:
        # Handle non-hyphenated UUIDs by converting to hyphenated format
        code_id = str(uuid.UUID(code_id))
    
    return db.query(VerificationCode).filter(VerificationCode.id == code_id).first()

def create_verification_code(db: Session, code: VerificationCodeCreate):
    """
    Create a new verification code record.
    
    This function is critical for the consent verification process, creating the
    verification codes that are sent to users to confirm their identity before
    processing consent actions. This verification step is essential for establishing
    valid consent under regulations like GDPR and CCPA, as it provides proof that
    the individual who claims to own a contact method actually has access to it.
    
    The verification process helps prevent fraudulent opt-ins and unauthorized
    preference changes, protecting both users and the organization. It creates an
    audit trail that demonstrates the organization took reasonable steps to verify
    the identity of individuals before processing their consent.
    
    Args:
        db (Session): SQLAlchemy database session.
        code (VerificationCodeCreate): Verification code creation data including
                                     user ID, code value, channel, expiration time,
                                     and purpose.
        
    Returns:
        VerificationCode: Created verification code object with tracking metadata.
    """
    db_code = VerificationCode(**code.model_dump())
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

def update_verification_code(db: Session, db_code: VerificationCode, code_update: VerificationCodeUpdate):
    """
    Update an existing verification code record.
    
    This function is primarily used to update the status of verification codes
    when they are verified or expire. Tracking these status changes is essential
    for security and compliance, as it prevents codes from being used multiple
    times or after expiration, which could lead to unauthorized access or
    fraudulent consent records.
    
    When a user successfully verifies a code, this function updates the record
    with the verification timestamp and changes the status to 'verified', creating
    a clear audit trail of when verification occurred. This timestamp is important
    for establishing when consent was confirmed, which may be required for
    regulatory compliance.
    
    Args:
        db (Session): SQLAlchemy database session.
        db_code (VerificationCode): Existing verification code object to update.
        code_update (VerificationCodeUpdate): Update data, typically status and
                                           verification timestamp.
        
    Returns:
        VerificationCode: Updated verification code object with new status.
    """
    for key, value in code_update.model_dump(exclude_unset=True).items():
        setattr(db_code, key, value)
    db.commit()
    db.refresh(db_code)
    return db_code

def delete_verification_code(db: Session, db_code: VerificationCode):
    """
    Delete a verification code record.
    
    This function should be used with caution, as verification codes are part of
    the consent audit trail. In most cases, it's preferable to let codes expire
    naturally and remain in the database as a record of the verification attempt,
    rather than deleting them.
    
    However, this function may be useful for data management purposes, such as
    cleaning up expired codes after a certain retention period to reduce database
    size. It might also be used in response to data deletion requests under
    privacy regulations like GDPR's "right to be forgotten."
    
    Args:
        db (Session): SQLAlchemy database session.
        db_code (VerificationCode): VerificationCode object to delete.
        
    Returns:
        None
    """
    db.delete(db_code)
    db.commit()
