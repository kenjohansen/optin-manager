"""
crud/auth_user.py

CRUD operations for AuthUser (authentication user) model.

This module provides database operations for managing authenticated users in the
OptIn Manager system. These operations support the role-based access control system,
where users can have different roles (Admin, Support) with varying permission levels.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.auth_user import AuthUser
from app.schemas.auth_user import AuthUserCreate, AuthUserUpdate
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_auth_user(db: Session, user_id):
    """
    Retrieve a specific authenticated user by their ID.
    
    This function supports both string UUIDs and integer IDs for backward compatibility,
    allowing the system to work with different ID formats without modification.
    
    Args:
        db (Session): SQLAlchemy database session
        user_id: User's unique identifier (can be string UUID or integer)
        
    Returns:
        AuthUser: The user record if found, None otherwise
    """
    # Handle both integer and string IDs
    return db.query(AuthUser).filter(AuthUser.id == user_id).first()

def get_auth_user_by_username(db: Session, username: str):
    """
    Retrieve a specific authenticated user by their username.
    
    This function is primarily used for authentication, allowing the system to
    look up users by their username during the login process.
    
    Args:
        db (Session): SQLAlchemy database session
        username (str): User's unique username
        
    Returns:
        AuthUser: The user record if found, None otherwise
    """
    return db.query(AuthUser).filter(AuthUser.username == username).first()

def get_auth_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a paginated list of authenticated users.
    
    This function supports the user management interface, allowing administrators
    to view and manage all authenticated users in the system. Pagination is
    implemented to handle large numbers of users efficiently.
    
    Args:
        db (Session): SQLAlchemy database session
        skip (int): Number of records to skip (for pagination)
        limit (int): Maximum number of records to return
        
    Returns:
        List[AuthUser]: List of user records
    """
    return db.query(AuthUser).offset(skip).limit(limit).all()

def create_auth_user(db: Session, user: AuthUserCreate):
    """
    Create a new authenticated user in the system.
    
    This function securely hashes the provided password before storing it in the
    database, ensuring that raw passwords are never stored. The role assigned to
    the user determines their permission level in the system.
    
    As noted in the memories, the system supports two main roles:
    - Admin: Can create campaigns/products and manage authenticated users
    - Support: Can view all pages but cannot create or manage resources
    
    Args:
        db (Session): SQLAlchemy database session
        user (AuthUserCreate): Pydantic schema with user creation data
        
    Returns:
        AuthUser: The newly created user record
    """
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
    """
    Update an existing authenticated user's information.
    
    This function allows for partial updates of user information, only modifying
    the fields that are provided in the update schema. If a new password is provided,
    it is securely hashed before storage.
    
    The ability to update user roles and active status is particularly important
    for access control management, allowing administrators to adjust permissions
    or temporarily disable accounts without deleting them.
    
    Args:
        db (Session): SQLAlchemy database session
        db_user (AuthUser): Existing user record to update
        user_update (AuthUserUpdate): Pydantic schema with update data
        
    Returns:
        AuthUser: The updated user record
    """
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
    """
    Delete an authenticated user from the system.
    
    This function permanently removes a user record from the database. In many cases,
    it's preferable to set is_active=False instead of deleting users, as this preserves
    the audit trail while preventing login. However, this delete function is provided
    for cases where complete removal is necessary.
    
    Args:
        db (Session): SQLAlchemy database session
        db_user (AuthUser): User record to delete
        
    Returns:
        None
    """
    db.delete(db_user)
    db.commit()
