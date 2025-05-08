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
    """
    Retrieve an opt-in program by its ID.
    
    This function is essential for accessing specific opt-in programs, which are
    the central entities for managing communication consent. Each opt-in program
    represents a specific type of communication that users can consent to receive.
    
    The flexible ID handling supports both string and UUID formats for backward
    compatibility, addressing the migration from UUID to string IDs noted in the
    memories. This ensures that opt-in programs can be retrieved regardless of
    how they were stored or referenced in different parts of the system.
    
    Args:
        db (Session): SQLAlchemy database session.
        optin_id: OptIn unique identifier (string or UUID).
        
    Returns:
        OptIn: OptIn object if found, else None.
    """
    # Handle both string and UUID inputs for backward compatibility
    if isinstance(optin_id, uuid.UUID):
        optin_id = str(optin_id)
    elif isinstance(optin_id, str) and '-' not in optin_id and len(optin_id) == 32:
        # Handle non-hyphenated UUIDs by converting to hyphenated format
        optin_id = str(uuid.UUID(optin_id))
    
    return db.query(OptIn).filter(OptIn.id == optin_id).first()


def list_optins(db: Session):
    """
    Retrieve a list of all opt-in programs ordered by creation date.
    
    This function supports the administrative interface for opt-in program management,
    allowing administrators to view and manage all available communication programs.
    The results are ordered by creation date (newest first) to prioritize recently
    created programs, which are more likely to be actively managed.
    
    Unlike other list functions, this one doesn't implement pagination because the
    number of opt-in programs is typically small and manageable. This simplifies
    the interface while still providing all necessary functionality.
    
    Args:
        db (Session): SQLAlchemy database session.
        
    Returns:
        List[OptIn]: List of all OptIn objects ordered by creation date (newest first).
    """
    return db.query(OptIn).order_by(OptIn.created_at.desc()).all()


def create_optin(db: Session, optin: OptInCreate):
    """
    Create a new opt-in program.
    
    This function is critical for setting up the foundation of consent management
    in the system. Opt-in programs define the specific types of communications that
    users can consent to receive, allowing for granular consent management as required
    by privacy regulations like GDPR and CCPA.
    
    Separating communications into distinct opt-in programs allows the organization to:
    1. Obtain specific, unbundled consent as required by regulations
    2. Apply different rules and workflows to different types of communications
    3. Track consent at a granular level for compliance reporting
    4. Allow users to manage their preferences for different communication types
    
    As noted in the memories, there was a migration from "Campaign/Product" to "OptIn"
    in the naming, but the core purpose remains the same: defining communication
    programs that users can opt into or out of.
    
    Args:
        db (Session): SQLAlchemy database session.
        optin (OptInCreate): OptIn creation data including name, type, description,
                           and status.
        
    Returns:
        OptIn: Created OptIn object with generated ID and timestamps.
    """
    db_optin = OptIn(**optin.model_dump())
    db.add(db_optin)
    db.commit()
    db.refresh(db_optin)
    return db_optin


def update_optin(db: Session, db_optin: OptIn, optin_update: OptInUpdate):
    """
    Update an existing opt-in program.
    
    This function allows administrators to modify opt-in programs as communication
    needs evolve. The most common updates include changing the description to clarify
    the purpose of the communications or updating the status to control whether the
    program is active, paused, archived, or closed.
    
    The ability to update opt-in programs without deleting them is essential for
    maintaining the integrity of the consent system. By changing the status rather
    than deleting records, the system preserves the relationship between opt-in
    programs and existing consent records, ensuring a complete audit trail for
    compliance purposes.
    
    Args:
        db (Session): SQLAlchemy database session.
        db_optin (OptIn): Existing OptIn object to update.
        optin_update (OptInUpdate): Update data with modified fields.
        
    Returns:
        OptIn: Updated OptIn object with new values.
    """
    for key, value in optin_update.model_dump(exclude_unset=True).items():
        setattr(db_optin, key, value)
    db.commit()
    db.refresh(db_optin)
    return db_optin


"""
Note: We intentionally don't provide a delete function for OptIn records.

Instead, we manage their lifecycle through status changes (active, paused, archived, closed).
This approach is essential for regulatory compliance, as it ensures we maintain a
complete history of consent records and their relationship to opt-in programs.

Deleting opt-in programs would break the relationship with existing consent records,
making it impossible to demonstrate what users consented to at a specific point in time.
This could create significant compliance issues with regulations like GDPR and CCPA,
which require organizations to maintain records of consent.

By using status changes instead of deletion, we maintain data integrity while still
providing administrators with the ability to control which opt-in programs are active.
"""
