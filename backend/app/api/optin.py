"""
api/optin.py

OptIn API endpoints for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.optin import OptInCreate, OptInUpdate, OptInOut
from app.crud import optin as crud_optin
from app.core.database import get_db
from app.core.deps import require_admin_user, require_support_user
import uuid
from typing import List

router = APIRouter(prefix="/optins", tags=["optins"])

@router.get("/", response_model=List[OptInOut])
def list_optins(db: Session = Depends(get_db), current_user=Depends(require_support_user)):
    """List all opt-ins. (admin/support roles)"""
    return crud_optin.list_optins(db)

@router.post("/", response_model=OptInOut)
def create_optin(optin: OptInCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """Create a new opt-in. (admin only)"""
    db_optin = crud_optin.create_optin(db, optin)
    return db_optin

@router.get("/{optin_id}", response_model=OptInOut)
def read_optin(optin_id: str, db: Session = Depends(get_db), current_user=Depends(require_support_user)):
    """Retrieve an opt-in by its ID. (admin/support roles)"""
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    return db_optin

@router.put("/{optin_id}", response_model=OptInOut)
def update_optin(optin_id: str, optin_update: OptInUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """Update an opt-in by its ID."""
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    return crud_optin.update_optin(db, db_optin, optin_update)

@router.put("/{optin_id}/pause")
def pause_optin(optin_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """Pause (inactivate) an opt-in program."""
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    
    # Update the status to paused
    from app.models.optin import OptInStatusEnum
    update_data = OptInUpdate(status=OptInStatusEnum.paused)
    updated_optin = crud_optin.update_optin(db, db_optin, update_data)
    
    return {"ok": True, "message": f"Opt-In '{updated_optin.name}' has been paused", "optin": updated_optin}

@router.put("/{optin_id}/resume")
def resume_optin(optin_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """Resume (activate) a paused opt-in program."""
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    
    # Update the status to active
    from app.models.optin import OptInStatusEnum
    update_data = OptInUpdate(status=OptInStatusEnum.active)
    updated_optin = crud_optin.update_optin(db, db_optin, update_data)
    
    return {"ok": True, "message": f"Opt-In '{updated_optin.name}' has been resumed", "optin": updated_optin}

@router.put("/{optin_id}/archive")
def archive_optin(optin_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """Archive an opt-in program (mark as no longer in use)."""
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    
    # Update the status to archived
    from app.models.optin import OptInStatusEnum
    update_data = OptInUpdate(status=OptInStatusEnum.archived)
    updated_optin = crud_optin.update_optin(db, db_optin, update_data)
    
    return {"ok": True, "message": f"Opt-In '{updated_optin.name}' has been archived", "optin": updated_optin}
