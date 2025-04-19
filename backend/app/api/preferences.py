"""
api/preferences.py

Preferences (opt-out/in) API endpoints for the OptIn Manager backend.
Implements Phase 1: send/verify code, fetch/update preferences for a contact.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from app.models.user import Contact
from app.models.campaign import Campaign
from app.models.consent import Consent, ConsentStatusEnum
from app.models.verification_code import VerificationCode, VerificationPurposeEnum, VerificationStatusEnum
from app.schemas.user import ContactOut
from app.core.database import get_db
from app.core.auth import create_access_token, oauth2_scheme
from jose import jwt, JWTError
from datetime import datetime, timedelta
import uuid, os

router = APIRouter(prefix="/contacts", tags=["preferences"])

# --- Helper: Find or create contact by email/phone ---
def get_or_create_contact(db: Session, contact: str):
    if "@" in contact:
        db_contact = db.query(Contact).filter(Contact.email == contact).first()
        if not db_contact:
            db_contact = Contact(email=contact)
            db.add(db_contact)
            db.commit()
            db.refresh(db_contact)
    else:
        db_contact = db.query(Contact).filter(Contact.phone == contact).first()
        if not db_contact:
            db_contact = Contact(phone=contact)
            db.add(db_contact)
            db.commit()
            db.refresh(db_contact)
    return db_contact

# --- 1. Send Verification Code ---
@router.post("/send-code")
def send_code(payload: dict = Body(...), db: Session = Depends(get_db)):
    contact_val = payload.get("contact")
    if not contact_val:
        raise HTTPException(status_code=400, detail="Missing contact")
    db_contact = get_or_create_contact(db, contact_val)
    # Generate code
    code = str(uuid.uuid4())[:6]
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    db_code = VerificationCode(
        user_id=db_contact.id,
        code=code,
        channel="email" if "@" in contact_val else "sms",
        sent_to=contact_val,
        expires_at=expires_at,
        purpose=VerificationPurposeEnum.opt_out,
        status=VerificationStatusEnum.pending
    )
    db.add(db_code)
    db.commit()
    # (Stub) Send code via email/SMS here
    return {"ok": True, "code": code if os.getenv("ENV") != "prod" else None}

# --- 2. Verify Code ---
@router.post("/verify-code")
def verify_code(payload: dict = Body(...), db: Session = Depends(get_db)):
    contact_val = payload.get("contact")
    code = payload.get("code")
    if not contact_val or not code:
        raise HTTPException(status_code=400, detail="Missing contact or code")
    db_contact = get_or_create_contact(db, contact_val)
    db_code = db.query(VerificationCode).filter(
        VerificationCode.user_id == db_contact.id,
        VerificationCode.code == code,
        VerificationCode.status == VerificationStatusEnum.pending,
        VerificationCode.expires_at > datetime.utcnow()
    ).first()
    if not db_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    db_code.status = VerificationStatusEnum.verified
    db_code.verified_at = datetime.utcnow()
    db.commit()
    # Issue JWT for preferences access (sub=contact_id)
    access_token = create_access_token(data={"sub": str(db_contact.id), "scope": "contact"})
    return {"ok": True, "token": access_token}

# --- 3. Get Preferences ---
@router.get("/preferences")
def get_preferences(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Validate JWT and extract contact_id
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "changeme"), algorithms=["HS256"])
        contact_id = payload.get("sub")
        if not contact_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    # List all campaigns
    campaigns = db.query(Campaign).all()
    consents = {c.campaign_id: c for c in db.query(Consent).filter(Consent.user_id == contact_id).all()}
    programs = []
    for camp in campaigns:
        consent = consents.get(camp.id)
        opted_in = consent.status != ConsentStatusEnum.opt_out if consent else True
        programs.append({"id": str(camp.id), "name": camp.name, "opted_in": opted_in})
    return {"programs": programs}

# --- 4. Update Preferences ---
@router.patch("/preferences")
def update_preferences(payload: dict = Body(...), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        jwt_payload = jwt.decode(token, os.getenv("SECRET_KEY", "changeme"), algorithms=["HS256"])
        contact_id = jwt_payload.get("sub")
        if not contact_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Save comment if provided
    comment = payload.get("comment")
    if comment is not None:
        db_contact.comment = comment

    # Handle global opt-out if requested
    global_opt_out = payload.get("global_opt_out", False)
    if global_opt_out:
        # Set all consents for this contact to opt-out
        consents = db.query(Consent).filter(Consent.user_id == contact_id).all()
        for consent in consents:
            consent.status = ConsentStatusEnum.opt_out
            consent.revoked_timestamp = datetime.utcnow()
        db.commit()
        return {"ok": True, "global_opt_out": True}

    # Otherwise, update per-program preferences
    programs = payload.get("programs", [])
    for prog in programs:
        camp_id = prog["id"]
        opted_in = prog["opted_in"]
        consent = db.query(Consent).filter(Consent.user_id == contact_id, Consent.campaign_id == camp_id).first()
        if consent:
            consent.status = ConsentStatusEnum.opt_in if opted_in else ConsentStatusEnum.opt_out
            consent.consent_timestamp = datetime.utcnow() if opted_in else None
            consent.revoked_timestamp = None if opted_in else datetime.utcnow()
        else:
            # Prevent opt-in to closed campaigns
            campaign = db.query(Campaign).filter(Campaign.id == camp_id).first()
            if opted_in and campaign and campaign.status == 'closed':
                raise HTTPException(status_code=400, detail="Cannot opt in to a closed campaign.")
            consent = Consent(
                user_id=contact_id,
                campaign_id=camp_id,
                channel="email",
                status=ConsentStatusEnum.opt_in if opted_in else ConsentStatusEnum.opt_out,
                consent_timestamp=datetime.utcnow() if opted_in else None,
                revoked_timestamp=None if opted_in else datetime.utcnow()
            )
            db.add(consent)
    db.commit()
    return {"ok": True}
