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
#   As noted in the memories, the backend must support SQLite for development
#   and testing, not PostgreSQL. This is a critical requirement.
# - Override via env/Helm for PostgreSQL or external DB in production
# - Use check_same_thread only for SQLite (required for SQLite to work with FastAPI)
# - No in-memory DB for production (would lose data between restarts)
from app.core.config import settings

# Get database URL from settings with fallback to SQLite
# This ensures the application works even without explicit configuration
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL or "sqlite:///./optin_manager.db"
print(f"[DEBUG] Using database URL: {SQLALCHEMY_DATABASE_URL}")

# Create SQLAlchemy engine with appropriate connection arguments
# The check_same_thread=False is required for SQLite to work with FastAPI's async model
# This allows multiple requests to use the same SQLite connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory with conservative settings
# - autocommit=False: Explicit transaction management for better control
# - autoflush=False: Don't automatically flush changes to DB, allowing for batching
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
# All models will inherit from this class to be part of the ORM
Base = declarative_base()

# Auto-create SQLite database file and tables if they don't exist
# This simplifies development and testing by creating the schema automatically
# In production, Alembic migrations should be used instead for schema management
db_path = SQLALCHEMY_DATABASE_URL.replace('sqlite:///', '')
if db_path and not os.path.exists(db_path):
    print(f"[DEBUG] Creating new SQLite DB and all tables at {db_path}")
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Yields a SQLAlchemy database session and ensures it's properly closed after use.
    
    This function implements the dependency injection pattern for database sessions
    in FastAPI. It creates a new session for each request, yields it to the endpoint
    function, and ensures it's properly closed afterward, even if exceptions occur.
    
    This pattern is essential for proper resource management and connection pooling,
    preventing connection leaks that could degrade performance or cause the
    application to run out of database connections.
    
    Usage:
        # As a FastAPI dependency
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        
        # Or with a context manager
        with next(get_db()) as db:
            items = db.query(Item).all()
    
    Yields:
        db (Session): SQLAlchemy session object connected to the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
