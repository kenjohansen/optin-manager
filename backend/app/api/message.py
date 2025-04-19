"""
api/message.py

Message API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.message import MessageCreate, MessageUpdate, MessageOut
from app.crud import message as crud_message
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/messages", tags=["messages"])

from fastapi import Body
from app.schemas.user import ContactOut as UserOut, ContactCreate as UserCreate
from app.crud.user import create_contact, update_contact, delete_contact
from app.schemas.campaign import CampaignOut
from app.schemas.consent import ConsentOut, ConsentCreate
from app.crud.consent import create_consent
from app.schemas.verification_code import VerificationCodeOut

from app.models.consent import Consent, ConsentStatusEnum
from app.models.message import MessageStatusEnum
from pydantic import BaseModel
from typing import Optional

class SendMessageRequest(BaseModel):
    recipient: str
    messageType: str
    content: str
    campaignId: Optional[uuid.UUID] = None
    optInFlow: Optional[dict] = None

class SendMessageResponse(BaseModel):
    message_id: uuid.UUID
    status: str
    opt_in_status: Optional[str] = None
    detail: Optional[str] = None

@router.post("/send", response_model=SendMessageResponse)
def send_message(
    payload: SendMessageRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Consent-aware message delivery endpoint.
    Implements PRD/Phase 1 logic:
    - Checks recipient opt-in status
    - If opted in: sends message immediately
    - If not opted in: creates pending message, triggers opt-in flow
    Args:
        payload (SendMessageRequest): Message send request.
        db (Session): SQLAlchemy database session.
    Returns:
        SendMessageResponse: Message delivery status and info.
    """
    # 1. Lookup contact by recipient (phone/email)
    from app.models.user import Contact
    user = db.query(Contact).filter((Contact.phone == payload.recipient) | (Contact.email == payload.recipient)).first()
    if not user:
        # Auto-create contact for new recipient
        user_in = UserCreate(phone=payload.recipient if payload.recipient.startswith('+') else None,
                             email=payload.recipient if '@' in payload.recipient else None)
        user = create_contact(db, user_in)
    # 2. Lookup consent for user/campaign/channel
    consent = db.query(Consent).filter(
        Consent.user_id == user.id,
        Consent.campaign_id == payload.campaignId if payload.campaignId else True,
        Consent.channel == "sms"
    ).order_by(Consent.consent_timestamp.desc()).first()
    if consent and consent.status == ConsentStatusEnum.opt_in:
        # User is opted in, send message immediately
        message_in = MessageCreate(
            user_id=user.id,
            campaign_id=payload.campaignId,
            channel="sms",
            content=payload.content,
            status=MessageStatusEnum.sent
        )
        message = crud_message.create_message(db, message_in)
        return SendMessageResponse(
            message_id=message.id,
            status="sent",
            opt_in_status="opt-in",
            detail="Message sent."
        )
    else:
        # Not opted in: create pending message, trigger opt-in flow
        message_in = MessageCreate(
            user_id=user.id,
            campaign_id=payload.campaignId,
            channel="sms",
            content=payload.content,
            status=MessageStatusEnum.pending
        )
        message = crud_message.create_message(db, message_in)
        # Block sending messages to closed campaigns
        if payload.campaignId is not None:
            from app.models.campaign import Campaign
            campaign = db.query(Campaign).filter(Campaign.id == payload.campaignId).first()
            if campaign and campaign.status == 'closed':
                raise HTTPException(status_code=400, detail="Cannot send message to a closed campaign.")
        # (Phase 1: send opt-in SMS here, mark consent as pending)
        # ... (placeholder for SMS gateway integration)
        # Create/update consent record
        if not consent:
            consent_in = ConsentCreate(
                user_id=user.id,
                campaign_id=payload.campaignId,
                channel="sms",
                status=ConsentStatusEnum.pending
            )
            create_consent(db, consent_in)
        return SendMessageResponse(
            message_id=message.id,
            status="pending",
            opt_in_status="pending",
            detail="User not opted in. Opt-in request sent."
        )

@router.post("/", response_model=MessageOut)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """
    Create a new message.
    Args:
        message (MessageCreate): Message creation data.
        db (Session): SQLAlchemy database session.
    Returns:
        MessageOut: Created message object.
    """
    db_message = crud_message.create_message(db, message)
    # Fetch opt-in status from Consent
    from app.crud import consent as crud_consent
    consent = db.query(crud_consent.Consent).filter(
        crud_consent.Consent.user_id == db_message.user_id,
        crud_consent.Consent.channel == db_message.channel,
        crud_consent.Consent.campaign_id == db_message.campaign_id
    ).order_by(crud_consent.Consent.consent_timestamp.desc()).first()
    opt_in_status = consent.status if consent else "pending"
    return {
        **db_message.__dict__,
        "opt_in_status": opt_in_status
    }

@router.get("/{message_id}", response_model=MessageOut)
def read_message(message_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a message by its ID, including opt-in status, delivery status, and timeline.
    Args:
        message_id (uuid.UUID): Message unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        MessageOut: Message object if found.
    Raises:
        HTTPException: 404 if message not found.
    """
    db_message = crud_message.get_message(db, message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    # Fetch opt-in status from Consent
    from app.crud import consent as crud_consent
    consent = db.query(crud_consent.Consent).filter(
        crud_consent.Consent.user_id == db_message.user_id,
        crud_consent.Consent.channel == db_message.channel,
        crud_consent.Consent.campaign_id == db_message.campaign_id
    ).order_by(crud_consent.Consent.consent_timestamp.desc()).first()
    opt_in_status = consent.status if consent else "pending"
    # Delivery status from message
    delivery_status = db_message.delivery_status
    # Timeline (simplified: consent + message events)
    timeline = []
    if consent:
        timeline.append({
            "event": f"consent_{consent.status}",
            "timestamp": str(consent.consent_timestamp) if consent.consent_timestamp else None
        })
    if db_message.sent_at:
        timeline.append({
            "event": f"message_{db_message.status}",
            "timestamp": str(db_message.sent_at)
        })
    else:
        timeline.append({
            "event": f"message_{db_message.status}",
            "timestamp": None
        })
    return {
        **db_message.__dict__,
        "opt_in_status": opt_in_status,
        "delivery_status": delivery_status,
        "timeline": timeline
    }

@router.put("/{message_id}", response_model=MessageOut)
def update_message(message_id: uuid.UUID, message_update: MessageUpdate, db: Session = Depends(get_db)):
    """
    Update a message by its ID.
    Args:
        message_id (uuid.UUID): Message unique identifier.
        message_update (MessageUpdate): Update data.
        db (Session): SQLAlchemy database session.
    Returns:
        MessageOut: Updated message object.
    Raises:
        HTTPException: 404 if message not found.
    """
    db_message = crud_message.get_message(db, message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    updated = crud_message.update_message(db, db_message, message_update)
    # Fetch opt-in status from Consent
    from app.crud import consent as crud_consent
    consent = db.query(crud_consent.Consent).filter(
        crud_consent.Consent.user_id == updated.user_id,
        crud_consent.Consent.channel == updated.channel,
        crud_consent.Consent.campaign_id == updated.campaign_id
    ).order_by(crud_consent.Consent.consent_timestamp.desc()).first()
    opt_in_status = consent.status if consent else "pending"
    return {
        **updated.__dict__,
        "opt_in_status": opt_in_status
    }

@router.delete("/{message_id}")
def delete_message(message_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a message by its ID.
    Args:
        message_id (uuid.UUID): Message unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        dict: {"ok": True} on successful deletion.
    Raises:
        HTTPException: 404 if message not found.
    """
    db_message = crud_message.get_message(db, message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    crud_message.delete_message(db, db_message)
    return {"ok": True}
