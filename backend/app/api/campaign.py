"""
api/campaign.py

Campaign API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import require_admin_user
from sqlalchemy.orm import Session
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignOut
from app.crud import campaign as crud_campaign
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignOut)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Create a new campaign.
    Args:
        campaign (CampaignCreate): Campaign creation data.
        db (Session): SQLAlchemy database session.
    Returns:
        CampaignOut: Created campaign object.
    """
    db_campaign = crud_campaign.create_campaign(db, campaign)
    return db_campaign

@router.get("/{campaign_id}", response_model=CampaignOut)
def read_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Retrieve a campaign by its ID.
    Args:
        campaign_id (uuid.UUID): Campaign unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        CampaignOut: Campaign object if found.
    Raises:
        HTTPException: 404 if campaign not found.
    """
    db_campaign = crud_campaign.get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign

@router.put("/{campaign_id}", response_model=CampaignOut)
def update_campaign(campaign_id: uuid.UUID, campaign_update: CampaignUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Update a campaign by its ID.
    Args:
        campaign_id (uuid.UUID): Campaign unique identifier.
        campaign_update (CampaignUpdate): Update data.
        db (Session): SQLAlchemy database session.
    Returns:
        CampaignOut: Updated campaign object.
    Raises:
        HTTPException: 404 if campaign not found.
    """
    db_campaign = crud_campaign.get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return crud_campaign.update_campaign(db, db_campaign, campaign_update)

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Delete a campaign by its ID.
    Args:
        campaign_id (uuid.UUID): Campaign unique identifier.
        db (Session): SQLAlchemy database session.
    Returns:
        dict: {"ok": True} on successful deletion.
    Raises:
        HTTPException: 404 if campaign not found.
    """
    db_campaign = crud_campaign.get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    crud_campaign.delete_campaign(db, db_campaign)
    return {"ok": True}
