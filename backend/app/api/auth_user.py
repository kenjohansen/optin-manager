"""
api/auth_user.py

API endpoints for authentication user (admin/staff/service accounts) management.
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

@router.post("/", response_model=AuthUserOut)
def create_auth_user(user: AuthUserCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    if crud_auth_user.get_auth_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = crud_auth_user.create_auth_user(db, user)
    return db_user

@router.get("/{user_id}", response_model=AuthUserOut)
def read_auth_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    db_user = crud_auth_user.get_auth_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=AuthUserOut)
def update_auth_user(user_id: uuid.UUID, user_update: AuthUserUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    db_user = crud_auth_user.get_auth_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_auth_user.update_auth_user(db, db_user, user_update)

@router.delete("/{user_id}")
def delete_auth_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_admin_user)):
    db_user = crud_auth_user.get_auth_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    crud_auth_user.delete_auth_user(db, db_user)
    return {"ok": True}
