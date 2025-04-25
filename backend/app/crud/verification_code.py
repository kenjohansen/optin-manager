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
    Args:
        db (Session): SQLAlchemy database session.
        code (VerificationCodeCreate): Verification code creation data.
    Returns:
        VerificationCode: Created verification code object.
    """
    db_code = VerificationCode(**code.model_dump())
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

def update_verification_code(db: Session, db_code: VerificationCode, code_update: VerificationCodeUpdate):
    """
    Update an existing verification code record.
    Args:
        db (Session): SQLAlchemy database session.
        db_code (VerificationCode): VerificationCode object to update.
        code_update (VerificationCodeUpdate): Update data.
    Returns:
        VerificationCode: Updated verification code object.
    """
    for key, value in code_update.model_dump(exclude_unset=True).items():
        setattr(db_code, key, value)
    db.commit()
    db.refresh(db_code)
    return db_code

def delete_verification_code(db: Session, db_code: VerificationCode):
    """
    Delete a verification code record.
    Args:
        db (Session): SQLAlchemy database session.
        db_code (VerificationCode): VerificationCode object to delete.
    Returns:
        None
    """
    db.delete(db_code)
    db.commit()
