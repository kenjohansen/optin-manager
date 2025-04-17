"""
schemas/auth_user.py

Pydantic schemas for authentication users (admin/staff/service accounts).
"""

from pydantic import BaseModel, Field
from typing import Optional
import uuid

class AuthUserBase(BaseModel):
    username: str
    role: str = "staff"
    is_active: bool = True

class AuthUserCreate(AuthUserBase):
    password: str

class AuthUserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class AuthUserOut(AuthUserBase):
    id: uuid.UUID
