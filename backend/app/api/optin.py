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
    """
    List all opt-ins available in the system.
    
    This endpoint provides a comprehensive view of all opt-in programs to help
    administrators and support staff monitor the overall opt-in landscape and make
    informed decisions about program management.
    
    Returns:
        List[OptInOut]: A list of all opt-in programs with their details
    
    Security:
        Requires admin or support role authentication
    """
    return crud_optin.list_optins(db)

@router.post("/", response_model=OptInOut)
def create_optin(optin: OptInCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Create a new opt-in program.
    
    This endpoint allows administrators to define new opt-in programs that users can
    subscribe to. Creating distinct opt-in programs enables organizations to manage
    different types of communications (promotional, transactional, alerts) separately
    and comply with regulatory requirements for specific consent management.
    
    Args:
        optin (OptInCreate): The opt-in program details to create
        
    Returns:
        OptInOut: The created opt-in program with generated ID and timestamps
        
    Security:
        Requires admin role authentication
    """
    db_optin = crud_optin.create_optin(db, optin)
    return db_optin

@router.get("/{optin_id}", response_model=OptInOut)
def read_optin(optin_id: str, db: Session = Depends(get_db), current_user=Depends(require_support_user)):
    """
    Retrieve detailed information about a specific opt-in program.
    
    This endpoint provides the ability to examine a single opt-in program's complete
    details, which is essential for auditing, troubleshooting, or reviewing the
    configuration of a specific program.
    
    Args:
        optin_id (str): The unique identifier of the opt-in program
        
    Returns:
        OptInOut: The opt-in program details
        
    Raises:
        HTTPException: 404 if the opt-in program is not found
        
    Security:
        Requires admin or support role authentication
    """
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    return db_optin

@router.put("/{optin_id}", response_model=OptInOut)
def update_optin(optin_id: str, optin_update: OptInUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Update an existing opt-in program's details.
    
    This endpoint allows administrators to modify opt-in program configurations as
    business needs evolve. The ability to update existing programs rather than creating
    new ones maintains historical continuity and preserves existing user consents.
    
    Args:
        optin_id (str): The unique identifier of the opt-in program to update
        optin_update (OptInUpdate): The updated opt-in program details
        
    Returns:
        OptInOut: The updated opt-in program
        
    Raises:
        HTTPException: 404 if the opt-in program is not found
        
    Security:
        Requires admin role authentication
    """
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    return crud_optin.update_optin(db, db_optin, optin_update)

@router.put("/{optin_id}/pause")
def pause_optin(optin_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """
    Pause an active opt-in program.
    
    This endpoint provides a way to temporarily suspend an opt-in program without
    deleting it. This is useful during maintenance periods, when reviewing program
    effectiveness, or when temporarily halting communications while preserving all
    user consents and program configurations.
    
    Args:
        optin_id (str): The unique identifier of the opt-in program to pause
        
    Returns:
        dict: Confirmation message and the updated opt-in program
        
    Raises:
        HTTPException: 404 if the opt-in program is not found
        
    Security:
        Requires admin role authentication
    """
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
    """
    Resume a paused opt-in program.
    
    This endpoint allows administrators to reactivate a previously paused program
    without having to recreate it. This maintains all existing user consents and
    program history while bringing the program back into active status.
    
    Args:
        optin_id (str): The unique identifier of the opt-in program to resume
        
    Returns:
        dict: Confirmation message and the updated opt-in program
        
    Raises:
        HTTPException: 404 if the opt-in program is not found
        
    Security:
        Requires admin role authentication
    """
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
    """
    Archive an opt-in program that is no longer needed.
    
    This endpoint provides a way to retire opt-in programs that are no longer relevant
    while preserving their data for historical, compliance, and audit purposes. Archiving
    rather than deleting ensures data retention policies can be properly enforced.
    
    Args:
        optin_id (str): The unique identifier of the opt-in program to archive
        
    Returns:
        dict: Confirmation message and the updated opt-in program
        
    Raises:
        HTTPException: 404 if the opt-in program is not found
        
    Security:
        Requires admin role authentication
    """
    db_optin = crud_optin.get_optin(db, optin_id)
    if not db_optin:
        raise HTTPException(status_code=404, detail="Opt-In not found")
    
    # Update the status to archived
    from app.models.optin import OptInStatusEnum
    update_data = OptInUpdate(status=OptInStatusEnum.archived)
    updated_optin = crud_optin.update_optin(db, db_optin, update_data)
    
    return {"ok": True, "message": f"Opt-In '{updated_optin.name}' has been archived", "optin": updated_optin}
