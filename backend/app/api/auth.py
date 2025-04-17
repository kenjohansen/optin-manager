"""
API endpoints for authentication and code verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.auth import verify_password, get_password_hash, create_access_token, oauth2_scheme
from app.schemas.auth import Token
from app.core.config import settings
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

# Dummy admin user (replace with DB lookup in production)
ADMIN_USER = {
    "username": "admin",
    "hashed_password": get_password_hash("adminpass")
}

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Replace with DB lookup for admin user
    if form_data.username != ADMIN_USER["username"] or not verify_password(form_data.password, ADMIN_USER["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": form_data.username, "scope": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify_code", response_model=Token)
def verify_code(
    code: str = Body(..., embed=True),
    sent_to: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Verify a submitted code against the database, mark as verified if valid, and issue a token.
    Args:
        code (str): Verification code value.
        sent_to (str): Contact (phone/email) code was sent to.
        db (Session): SQLAlchemy database session.
    Returns:
        Token: JWT access token if verification succeeds.
    Raises:
        HTTPException: 400 if code is invalid or expired.
    """
    from app.models.verification_code import VerificationCode, VerificationStatusEnum
    from datetime import datetime
    db_code = db.query(VerificationCode).filter(
        VerificationCode.code == code,
        VerificationCode.sent_to == sent_to,
        VerificationCode.status == VerificationStatusEnum.pending
    ).order_by(VerificationCode.expires_at.desc()).first()
    if not db_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    if db_code.expires_at < datetime.utcnow():
        db_code.status = VerificationStatusEnum.expired
        db.commit()
        raise HTTPException(status_code=400, detail="Code expired")
    # Mark as verified
    db_code.status = VerificationStatusEnum.verified
    db_code.verified_at = datetime.utcnow()
    db.commit()
    # Issue a token (scope: contact, sub: sent_to)
    access_token = create_access_token(data={"sub": db_code.sent_to, "scope": "contact"})
    return {"access_token": access_token, "token_type": "bearer"}
