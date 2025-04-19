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

from typing import List
router = APIRouter(prefix="/campaigns", tags=["campaigns"])

from app.core.deps import require_admin_user, require_support_user

@router.get("/", response_model=List[CampaignOut])
def list_campaigns(db: Session = Depends(get_db), current_user=Depends(require_support_user)):
    """
    List all campaigns. (admin/support roles)
    """
    return crud_campaign.list_campaigns(db)

@router.get("", response_model=List[CampaignOut], include_in_schema=False)
def list_campaigns_noslash(db: Session = Depends(get_db), current_user=Depends(require_support_user)):
    return crud_campaign.list_campaigns(db)

@router.post("/", response_model=CampaignOut)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Create a new campaign. (admin only)
    """
    db_campaign = crud_campaign.create_campaign(db, campaign)
    return db_campaign

@router.post("", response_model=CampaignOut, include_in_schema=False)
def create_campaign_noslash(campaign: CampaignCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    return crud_campaign.create_campaign(db, campaign)

@router.get("/{campaign_id}", response_model=CampaignOut)
def read_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_support_user)):
    """
    Retrieve a campaign by its ID. (admin/support roles)
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

@router.put("/{campaign_id}/update-name-and-status", response_model=CampaignOut)
def update_campaign_name_and_status(campaign_id: uuid.UUID, campaign_update: CampaignUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Update a campaign's name and/or status by its ID.
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
    if campaign_update.status == 'closed':
        db_campaign.status = campaign_update.status
    if campaign_update.name:
        db_campaign.name = campaign_update.name
    db.commit()
    return db_campaign

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
