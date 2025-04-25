"""
crud/optin.py

CRUD operations for the OptIn model in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
from sqlalchemy.orm import Session
from app.models.optin import OptIn
from app.schemas.optin import OptInCreate, OptInUpdate
import uuid


def get_optin(db: Session, optin_id):
    # Handle both string and UUID inputs for backward compatibility
    if isinstance(optin_id, uuid.UUID):
        optin_id = str(optin_id)
    elif isinstance(optin_id, str) and '-' not in optin_id and len(optin_id) == 32:
        # Handle non-hyphenated UUIDs by converting to hyphenated format
        optin_id = str(uuid.UUID(optin_id))
    
    return db.query(OptIn).filter(OptIn.id == optin_id).first()


def list_optins(db: Session):
    return db.query(OptIn).order_by(OptIn.created_at.desc()).all()


def create_optin(db: Session, optin: OptInCreate):
    db_optin = OptIn(**optin.model_dump())
    db.add(db_optin)
    db.commit()
    db.refresh(db_optin)
    return db_optin


def update_optin(db: Session, db_optin: OptIn, optin_update: OptInUpdate):
    for key, value in optin_update.model_dump(exclude_unset=True).items():
        setattr(db_optin, key, value)
    db.commit()
    db.refresh(db_optin)
    return db_optin


# Note: We don't provide a delete function for OptIn records
# Instead, we manage their lifecycle through status changes (active, paused, archived)
# This ensures we maintain a complete history of consent records for compliance purposes
