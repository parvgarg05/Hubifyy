"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass


# Create database engine
# Check if we are using SQLite (the URL starts with "sqlite")
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False}  # <--- REQUIRED for SQLite
    )
else:
    engine = create_engine(settings.DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
