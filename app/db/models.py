"""
SQLAlchemy ORM Models for Hubify application.
Uses SQLAlchemy 2.0 style with type hints and Mapped columns.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List

from sqlalchemy import String, Text, DateTime, Enum as SQLEnum, ForeignKey, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserRole(str, Enum):
    """Enum for user roles."""
    STUDENT = "student"
    ADMIN = "admin"


# Association table for Many-to-Many relationship between User and Event
event_registration = Table(
    "event_registration",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("registration_date", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)


class User(Base):
    """
    User model representing a student or admin.
    """
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    clubs_admin: Mapped[List["Club"]] = relationship(
        "Club",
        back_populates="admin",
        foreign_keys="Club.admin_id",
        cascade="all, delete-orphan"
    )
    registered_events: Mapped[List["Event"]] = relationship(
        "Event",
        secondary=event_registration,
        back_populates="registered_users"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"


class Club(Base):
    """
    Club model representing a college club.
    """
    __tablename__ = "club"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    admin: Mapped["User"] = relationship(
        "User",
        back_populates="clubs_admin",
        foreign_keys=[admin_id]
    )
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="club",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Club(id={self.id}, name='{self.name}', admin_id={self.admin_id})>"


class Event(Base):
    """
    Event model representing a club event.
    """
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # NEW FIELD: Stores the Google Form link
    registration_link: Mapped[str] = mapped_column(String(1000), nullable=True) 

    club_id: Mapped[int] = mapped_column(ForeignKey("club.id"), nullable=False)

    # Relationships
    club: Mapped["Club"] = relationship(
        "Club",
        back_populates="events",
        foreign_keys=[club_id]
    )
    registered_users: Mapped[List["User"]] = relationship(
        "User",
        secondary=event_registration,
        back_populates="registered_events"
    )

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title='{self.title}', club_id={self.club_id})>"
