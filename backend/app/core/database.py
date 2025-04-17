"""
core/database.py

Database engine and session management for OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# DATABASE_URL logic:
# - Default: file-based SQLite for local/dev (sqlite:///./optin_manager.db)
# - Override via env/Helm for PostgreSQL or external DB
# - Use check_same_thread only for SQLite
# - No in-memory DB for production
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL or "sqlite:///./optin_manager.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Yields a SQLAlchemy database session.
    Ensures the session is closed after use.
    Usage:
        with get_db() as db:
            ...
    Yields:
        db (Session): SQLAlchemy session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
