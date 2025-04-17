"""
Dependency functions for authentication and authorization in OptIn Manager backend.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.auth import TokenData
from app.core.auth import oauth2_scheme

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# Dependency to get the current user (admin or contact)
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        scope: str = payload.get("scope")
        if username is None or scope is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(username=username, scope=scope)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to require admin scope
def require_admin_user(current_user: TokenData = Depends(get_current_user)):
    if current_user.scope != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# Dependency to require contact scope (verified contact)
def require_verified_contact(current_user: TokenData = Depends(get_current_user)):
    if current_user.scope != "contact":
        raise HTTPException(status_code=403, detail="Contact verification required")
    return current_user
