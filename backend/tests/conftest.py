"""
conftest.py

Pytest fixtures for OptIn Manager backend tests.
"""
import pytest
import os

@pytest.fixture(scope="session", autouse=True)
def ensure_uploads_dir():
    os.makedirs("static/uploads", exist_ok=True)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import app.core.database as core_db
from app.core.database import Base

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
core_db.engine = engine
core_db.SessionLocal = TestingSessionLocal
# Import all models to register tables - ensure all models are included
# Note: The model for contacts is actually named 'user.py' in the codebase

# Explicitly import all models to ensure they're registered with SQLAlchemy
import app.models.consent
import app.models.optin
import app.models.message
import app.models.message_template
import app.models.verification_code
import app.models.contact  # This is the contact model
import app.models.auth_user
import app.models.customization
# Drop all tables first to ensure clean state
Base.metadata.drop_all(bind=engine)
# Create all tables
Base.metadata.create_all(bind=engine)
print("Tables after create_all:", Base.metadata.tables.keys())

@pytest.fixture
def db_session():
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_get_db(monkeypatch, db_session):
    from app.main import app
    def _get_db_override():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[core_db.get_db] = _get_db_override
    yield
    app.dependency_overrides = {}
