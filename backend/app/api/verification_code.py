"""
api/verification_code.py

VerificationCode API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from datetime import datetime, timedelta
import random
import string
from sqlalchemy.orm import Session
from app.schemas.verification_code import VerificationCodeCreate, VerificationCodeUpdate, VerificationCodeOut
from app.crud import verification_code as crud_code
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/verification-codes", tags=["verification_codes"])

@router.post("/send")
def send_verification_code(
    user_id: str = Body(...),
    channel: str = Body(...),
    sent_to: str = Body(...),
    purpose: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Generate and store a verification code for a user/channel, and (stub) send it.
    Args:
        user_id (uuid.UUID): User or contact id.
        channel (str): Channel to send code (sms/email).
        sent_to (str): Recipient contact (phone/email).
        purpose (str): Purpose of verification.
        db (Session): SQLAlchemy session.
    Returns:
        dict: {"ok": True, "code": <code>} (code is included for dev/testing only)
    """
    # Generate a random 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    code_create = VerificationCodeCreate(
        user_id=user_id,
        code=code,
        channel=channel,
        sent_to=sent_to,
        expires_at=expires_at,
        purpose=purpose,
        status="pending"
    )
    db_code = crud_code.create_verification_code(db, code_create)
    # Stub: Actually send code via SMS/email here
    # For now, just return the code for development/testing
    return {"ok": True, "code": code, "expires_at": expires_at}


@router.post("/", response_model=VerificationCodeOut)
def create_verification_code(code: VerificationCodeCreate, db: Session = Depends(get_db)):
    """
    Create a new verification code record.
    Args:
        code (VerificationCodeCreate): Verification code creation data.
        db (Session): SQLAlchemy database session.
    Returns:
        VerificationCodeOut: Created verification code object.
    """
    db_code = crud_code.create_verification_code(db, code)
    return db_code

@router.get("/{code_id}", response_model=VerificationCodeOut)
def read_verification_code(code_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a verification code record by its ID.
    Args:
        code_id (uuid.UUID): Verification code unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        VerificationCodeOut: Verification code object if found.
    Raises:
        HTTPException: 404 if verification code not found.
    """
    db_code = crud_code.get_verification_code(db, code_id)
    if not db_code:
        raise HTTPException(status_code=404, detail="Verification code not found")
    return db_code

@router.put("/{code_id}", response_model=VerificationCodeOut)
def update_verification_code(code_id: str, code_update: VerificationCodeUpdate, db: Session = Depends(get_db)):
    """
    Update a verification code record by its ID.
    Args:
        code_id (uuid.UUID): Verification code unique identifier.
        code_update (VerificationCodeUpdate): Update data.
        db (Session): SQLAlchemy database session.
    Returns:
        VerificationCodeOut: Updated verification code object.
    Raises:
        HTTPException: 404 if verification code not found.
    """
    db_code = crud_code.get_verification_code(db, code_id)
    if not db_code:
        raise HTTPException(status_code=404, detail="Verification code not found")
    return crud_code.update_verification_code(db, db_code, code_update)

@router.delete("/{code_id}", response_model=dict)
def delete_verification_code(code_id: str, db: Session = Depends(get_db)):
    """
    Delete a verification code record by its ID.
    Args:
        code_id (str): Verification code unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        dict: {"ok": True} on successful deletion.
    Raises:
        HTTPException: 404 if verification code not found.
    """
    db_code = crud_code.get_verification_code(db, code_id)
    if not db_code:
        raise HTTPException(status_code=404, detail="Verification code not found")
    crud_code.delete_verification_code(db, db_code)
    return {"ok": True}
