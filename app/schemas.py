"""
Pydantic schemas for request/response validation.
Uses Pydantic v2 with ConfigDict for ORM mode.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str
    role: str = "student"  # 'student' or 'admin'


class UserOut(UserBase):
    """Schema for user response (output)."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Token Schemas ====================

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: Optional[str] = None


# ==================== Club Schemas ====================

class ClubBase(BaseModel):
    """Base club schema with common fields."""
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class ClubCreate(ClubBase):
    """Schema for creating a new club."""
    pass


class ClubOut(ClubBase):
    """Schema for club response (output)."""
    id: int
    admin_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ClubResponse(ClubOut):
    """Backward-compatible club response schema used by routers."""
    pass


# ==================== Event Schemas ====================

class EventBase(BaseModel):
    """Base event schema with common fields."""
    title: str
    description: Optional[str] = None
    date_time: datetime
    location: str


class EventCreate(EventBase):
    """Schema for creating a new event."""
    club_id: int


class EventOut(EventBase):
    """Schema for event response (output)."""
    id: int
    club_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ClubDetailResponse(ClubResponse):
    """Detailed club payload including admin and related events."""
    admin: Optional[UserOut] = None
    events: list[EventOut] = Field(default_factory=list)
