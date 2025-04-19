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

router = APIRouter(tags=["auth"])

# Dummy admin user (replace with DB lookup in production)
ADMIN_USER = {
    "username": "admin",
    "hashed_password": get_password_hash("adminpass")
}

from app.models.auth_user import AuthUser

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # First, check if any users exist in the DB
    user_count = db.query(AuthUser).count()
    if user_count == 0:
        # Fallback to dummy admin if DB is empty
        if form_data.username == ADMIN_USER["username"] and verify_password(form_data.password, ADMIN_USER["hashed_password"]):
            access_token = create_access_token(data={"sub": form_data.username, "scope": "admin"})
            return Token(access_token=access_token, token_type="bearer", expires_in=3600)
        else:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
    # DB-backed authentication
    from app.crud.auth_user import get_auth_user_by_username
    user = get_auth_user_by_username(db, form_data.username)
    if not user or not user.is_active or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "scope": user.role})
    return Token(access_token=access_token, token_type="bearer", expires_in=3600)

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
    from app.schemas.auth import Token
    return Token(access_token=access_token, token_type="bearer", expires_in=3600)
