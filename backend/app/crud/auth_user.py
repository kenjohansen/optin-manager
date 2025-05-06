"""
crud/auth_user.py

CRUD operations for AuthUser (authentication user) model.
"""

from sqlalchemy.orm import Session
from app.models.auth_user import AuthUser
from app.schemas.auth_user import AuthUserCreate, AuthUserUpdate
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_auth_user(db: Session, user_id):
    # Handle both integer and string IDs
    return db.query(AuthUser).filter(AuthUser.id == user_id).first()

def get_auth_user_by_username(db: Session, username: str):
    return db.query(AuthUser).filter(AuthUser.username == username).first()

def get_auth_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AuthUser).offset(skip).limit(limit).all()

def create_auth_user(db: Session, user: AuthUserCreate):
    hashed_pw = pwd_context.hash(user.password)
    db_user = AuthUser(
        username=user.username,
        password_hash=hashed_pw,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_auth_user(db: Session, db_user: AuthUser, user_update: AuthUserUpdate):
    if user_update.password:
        db_user.password_hash = pwd_context.hash(user_update.password)
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.role:
        db_user.role = user_update.role
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_auth_user(db: Session, db_user: AuthUser):
    db.delete(db_user)
    db.commit()
