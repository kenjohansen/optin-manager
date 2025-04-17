"""
api/contact.py

Contact API endpoints for the OptIn Manager backend.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import ContactCreate, ContactUpdate, ContactOut
from app.crud import user as crud_contact
from app.core.database import get_db
import uuid

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/", response_model=ContactOut)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = crud_contact.create_contact(db, contact)
    return db_contact

@router.get("/{contact_id}", response_model=ContactOut)
def read_contact(contact_id: uuid.UUID, db: Session = Depends(get_db)):
    db_contact = crud_contact.get_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: uuid.UUID, contact_update: ContactUpdate, db: Session = Depends(get_db)):
    db_contact = crud_contact.get_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud_contact.update_contact(db, db_contact, contact_update)

@router.delete("/{contact_id}")
def delete_contact(contact_id: uuid.UUID, db: Session = Depends(get_db)):
    db_contact = crud_contact.get_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    crud_contact.delete_contact(db, db_contact)
    return {"ok": True}
