"""
Pydantic schemas for authentication and token handling.
"""
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = 3600

class TokenData(BaseModel):
    username: Optional[str] = None
    scope: Optional[str] = None
