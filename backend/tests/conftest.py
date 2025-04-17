"""
conftest.py

Pytest fixtures for OptIn Manager backend tests.
"""
import pytest
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
# Import all models to register tables
from app.models import user, consent, campaign, message, message_template, verification_code
Base.metadata.create_all(bind=engine)
print("Tables after create_all:", Base.metadata.tables)

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
