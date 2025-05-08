"""
api/auth_user.py

API endpoints for authentication user (admin/staff/service accounts) management.

This module provides the API endpoints for managing authenticated users with
role-based access control. It supports creating, reading, updating, and deleting
users with admin or support roles, as well as accessing related data like contacts
and message history.

As noted in the memories, the system supports two roles for authenticated users:
- Admin: Can create campaigns, products, and manage authenticated users
- Support: Can view all pages but cannot create campaigns/products or manage users

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth_user import AuthUserCreate, AuthUserUpdate, AuthUserOut
from app.crud import auth_user as crud_auth_user
from app.core.database import get_db
from app.core.deps import require_admin_user
import uuid

router = APIRouter(prefix="/auth_users", tags=["auth_users"])

from app.crud import contact as crud_contact, message as crud_message
from app.schemas.contact import ContactOut
from app.schemas.message import MessageOut
from fastapi import Query

@router.get("/contacts", response_model=list[ContactOut])
def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """List all contacts (subscribers)."""
    return crud_contact.list_contacts(db, skip=skip, limit=limit)

@router.get("/messages", response_model=list[MessageOut])
def list_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """List all messages (message history)."""
    return crud_message.list_messages(db, skip=skip, limit=limit)

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """Basic analytics: total contacts, opt-ins, messages sent."""
    total_contacts = db.query(crud_contact.Contact).count()
    total_opted_in = db.query(crud_contact.Contact).filter(crud_contact.Contact.status == "active").count()
    total_messages = db.query(crud_message.Message).count()
    return {
        "total_contacts": total_contacts,
        "total_opted_in": total_opted_in,
        "total_messages": total_messages
    }

from app.core.deps import require_admin_user

@router.get("/", response_model=list[AuthUserOut])
def list_auth_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    """List all authenticated users (admins and support staff)."""
    users = crud_auth_user.get_auth_users(db, skip=skip, limit=limit)
    # Convert user objects to dictionaries and ensure ID is a string
    result = []
    for user in users:
        user_dict = {
            "id": str(user.id),
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        result.append(user_dict)
    return result

@router.post("/", response_model=AuthUserOut)
def create_auth_user(user: AuthUserCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    if crud_auth_user.get_auth_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = crud_auth_user.create_auth_user(db, user)
    
    # Convert to dictionary with string ID
    return {
        "id": str(db_user.id),
        "username": db_user.username,
        "role": db_user.role,
        "is_active": db_user.is_active,
        "name": db_user.name,
        "email": db_user.email,
        "created_at": db_user.created_at
    }

@router.get("/{user_id}", response_model=AuthUserOut)
def read_auth_user(user_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    # Try to convert to integer if it's a numeric string
    try:
        if user_id.isdigit():
            user_id = int(user_id)
    except:
        pass
        
    db_user = crud_auth_user.get_auth_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Convert to dictionary with string ID
    return {
        "id": str(db_user.id),
        "username": db_user.username,
        "role": db_user.role,
        "is_active": db_user.is_active,
        "name": db_user.name,
        "email": db_user.email,
        "created_at": db_user.created_at
    }

@router.put("/{user_id}", response_model=AuthUserOut)
def update_auth_user(user_id: str, user_update: AuthUserUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    # Try to convert to integer if it's a numeric string
    try:
        if user_id.isdigit():
            user_id = int(user_id)
    except:
        pass
        
    db_user = crud_auth_user.get_auth_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    updated_user = crud_auth_user.update_auth_user(db, db_user, user_update)
    
    # Convert to dictionary with string ID
    return {
        "id": str(updated_user.id),
        "username": updated_user.username,
        "role": updated_user.role,
        "is_active": updated_user.is_active,
        "name": updated_user.name,
        "email": updated_user.email,
        "created_at": updated_user.created_at
    }

@router.delete("/{user_id}")
def delete_auth_user(user_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    # Try to convert to integer if it's a numeric string
    try:
        if user_id.isdigit():
            user_id = int(user_id)
    except:
        pass
        
    db_user = crud_auth_user.get_auth_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    crud_auth_user.delete_auth_user(db, db_user)
    return {"ok": True}
