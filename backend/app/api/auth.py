"""
api/auth.py

API endpoints for authentication and code verification.

This module provides the API endpoints for user authentication, including login,
password management, and verification code validation. It supports both authenticated
user login (admin/support roles) and contact verification through one-time codes.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.auth import verify_password, get_password_hash, create_access_token, oauth2_scheme, get_current_user
from app.schemas.auth import Token, PasswordResetRequest, ChangePasswordRequest
from app.schemas.auth_user import AuthUserUpdate
from app.core.config import settings
from app.core.database import get_db
import uuid
import os
from pydantic import EmailStr
from typing import Optional
from app.api.preferences import send_code
from app.crud import auth_user as crud_auth_user
import secrets
import string

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
    from datetime import datetime
    user = get_auth_user_by_username(db, form_data.username)
    if not user or not user.is_active or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Update last_login timestamp
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username, "scope": user.role})
    return Token(access_token=access_token, token_type="bearer", expires_in=3600)

@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request a password reset for an authenticated user."""
    # Find the user by username
    user = crud_auth_user.get_auth_user_by_username(db, request.username)
    
    # For security reasons, always return a success response even if user doesn't exist
    # This prevents username enumeration attacks
    if not user or not user.email:
        return {"message": "If the account exists, a password reset email has been sent."}
    
    # Generate a random reset token
    alphabet = string.ascii_letters + string.digits
    reset_token = ''.join(secrets.choice(alphabet) for _ in range(8))
    
    # Generate a temporary password
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Hash the new temporary password
    hashed_password = get_password_hash(temp_password)
    
    # Update the user's password in the database
    user_update = AuthUserUpdate(password=temp_password)
    crud_auth_user.update_auth_user(db, user, user_update)
    
    # Send the reset email with the temporary password
    # Use the contact's email address and the verification code system
    try:
        # Get the frontend URL from environment or use default
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        login_url = f"{frontend_url}/login"
        
        # Format the email message
        message = f"You requested a password reset for your OptIn Manager account.\n\n"
        message += f"Your temporary password is: {temp_password}\n\n"
        message += f"Please log in at: {login_url}\n\n"
        message += f"Use this temporary password and change it immediately after logging in.\n\n"
        message += f"If you did not request this password reset, please contact your administrator."
        
        # Send the email
        # Note: We're using the preferences.send_code function but with a custom message
        # This assumes the user has an email address stored in their profile
        send_code(
            db=db,
            payload={
                "contact": user.email,  # Changed from contact_value to contact
                "contact_type": "email",
                "code": temp_password,  # Using the temp password as the "code"
                "purpose": "password_reset",
                "preferences_url": "",  # No URL needed
                "custom_message": message,
                "auth_user_name": "System"
            }
        )
    except Exception as e:
        # Log the error but don't expose details to the client
        print(f"Error sending password reset email: {str(e)}")
    
    # Always return the same message regardless of success or failure
    # This prevents username enumeration attacks
    return {"message": "If the account exists, a password reset email has been sent."}

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for the authenticated user."""
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
    
    # Update password
    user_update = AuthUserUpdate(password=request.new_password)
    crud_auth_user.update_auth_user(db, current_user, user_update)
    
    return {"message": "Password changed successfully"}

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
