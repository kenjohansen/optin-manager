"""
crud/campaign.py

CRUD operations for the Campaign model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate
import uuid

def get_campaign(db: Session, campaign_id: uuid.UUID):
    """
    Retrieve a campaign by its ID.
    Args:
        db (Session): SQLAlchemy database session.
        campaign_id (uuid.UUID): Campaign unique identifier.
    Returns:
        Campaign: Campaign object if found, else None.
    """
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()

def create_campaign(db: Session, campaign: CampaignCreate):
    """
    Create a new campaign record.
    Args:
        db (Session): SQLAlchemy database session.
        campaign (CampaignCreate): Campaign creation data.
    Returns:
        Campaign: Created campaign object.
    """
    db_campaign = Campaign(**campaign.model_dump())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def update_campaign(db: Session, db_campaign: Campaign, campaign_update: CampaignUpdate):
    """
    Update an existing campaign record.
    Args:
        db (Session): SQLAlchemy database session.
        db_campaign (Campaign): Campaign object to update.
        campaign_update (CampaignUpdate): Update data.
    Returns:
        Campaign: Updated campaign object.
    """
    for key, value in campaign_update.model_dump(exclude_unset=True).items():
        setattr(db_campaign, key, value)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, db_campaign: Campaign):
    """
    Delete a campaign record.
    Args:
        db (Session): SQLAlchemy database session.
        db_campaign (Campaign): Campaign object to delete.
    Returns:
        None
    """
    db.delete(db_campaign)
    db.commit()

def list_campaigns(db: Session):
    """
    List all campaigns.
    Args:
        db (Session): SQLAlchemy database session.
    Returns:
        List[Campaign]: List of all Campaign objects.
    """
    return db.query(Campaign).all()

