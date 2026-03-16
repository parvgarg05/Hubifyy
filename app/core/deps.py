"""
Dependencies for authentication and database access.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db import models  # Correct import path

# This is just for Swagger UI support
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Retrieves the current user from the cookie OR the authorization header.
    """
    token = None

    # 1. Try to get the token from the "access_token" COOKIE (Browser)
    if "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    # 2. If no cookie, try the Authorization HEADER (Swagger UI / API tools)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    # 3. If no token found anywhere, reject access
    if not token:
        # OPTIONAL: You could return a RedirectResponse("/login") here instead of raising 401
        # if you want to auto-redirect users who aren't logged in.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Clean the token (Remove "Bearer " prefix if it was stored with it)
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    # 5. Decode the token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # 6. Find the user in the database
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """
    Dependency to ensure the user is an Admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return current_user

# Add this to the bottom of app/core/deps.py

def get_optional_user(request: Request, db: Session = Depends(get_db)):
    """
    Tries to get the current user. Returns None if not logged in.
    Does NOT raise an error (unlike get_current_user).
    """
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None