"""
tests/test_crud_customization.py

Unit tests for the customization CRUD operations.

These tests verify that the database operations for customization settings
work correctly, including retrieving, updating, and setting logo paths and colors.

"""

import pytest
from sqlalchemy.orm import Session
from app.crud.customization import get_customization, set_logo_path, set_colors
from app.models.customization import Customization


def test_get_customization_empty(db_session: Session):
    """Test retrieving customization settings when none exist."""
    # Ensure no customization exists
    db_session.query(Customization).delete()
    db_session.commit()
    
    # Get customization should return None
    result = get_customization(db_session)
    assert result is None


def test_get_customization_existing(db_session: Session):
    """Test retrieving customization settings when they exist."""
    # Create a customization record
    customization = Customization(
        company_name="Test Company",
        privacy_policy_url="https://example.com/privacy",
        primary_color="#123456",
        secondary_color="#abcdef"
    )
    db_session.add(customization)
    db_session.commit()
    
    # Get customization should return the record
    result = get_customization(db_session)
    assert result is not None
    assert result.company_name == "Test Company"
    assert result.privacy_policy_url == "https://example.com/privacy"
    assert result.primary_color == "#123456"
    assert result.secondary_color == "#abcdef"
    
    # Clean up
    db_session.delete(customization)
    db_session.commit()


def test_set_logo_path_new(db_session: Session):
    """Test setting a logo path when no customization record exists."""
    # Ensure no customization exists
    db_session.query(Customization).delete()
    db_session.commit()
    
    # Set logo path should create a new record
    logo_path = "/static/uploads/test_logo.png"
    result = set_logo_path(db_session, logo_path)
    
    # Verify the result
    assert result is not None
    assert result.logo_path == logo_path
    
    # Verify in database
    db_customization = db_session.query(Customization).first()
    assert db_customization is not None
    assert db_customization.logo_path == logo_path
    
    # Clean up
    db_session.delete(db_customization)
    db_session.commit()


def test_set_logo_path_existing(db_session: Session):
    """Test setting a logo path when customization record already exists."""
    # Create a customization record
    customization = Customization(
        company_name="Test Company",
        privacy_policy_url="https://example.com/privacy"
    )
    db_session.add(customization)
    db_session.commit()
    
    # Set logo path should update the existing record
    logo_path = "/static/uploads/test_logo.png"
    result = set_logo_path(db_session, logo_path)
    
    # Verify the result
    assert result is not None
    assert result.logo_path == logo_path
    assert result.company_name == "Test Company"  # Other fields should be preserved
    
    # Verify in database
    db_customization = db_session.query(Customization).first()
    assert db_customization is not None
    assert db_customization.logo_path == logo_path
    assert db_customization.company_name == "Test Company"  # Other fields should be preserved
    
    # Clean up
    db_session.delete(db_customization)
    db_session.commit()


def test_set_colors_new(db_session: Session):
    """Test setting colors when no customization record exists."""
    # Ensure no customization exists
    db_session.query(Customization).delete()
    db_session.commit()
    
    # Set colors should create a new record
    primary = "#111111"
    secondary = "#222222"
    result = set_colors(db_session, primary, secondary)
    
    # Verify the result
    assert result is not None
    assert result.primary_color == primary
    assert result.secondary_color == secondary
    
    # Verify in database
    db_customization = db_session.query(Customization).first()
    assert db_customization is not None
    assert db_customization.primary_color == primary
    assert db_customization.secondary_color == secondary
    
    # Clean up
    db_session.delete(db_customization)
    db_session.commit()


def test_set_colors_existing(db_session: Session):
    """Test setting colors when customization record already exists."""
    # Create a customization record
    customization = Customization(
        company_name="Test Company",
        privacy_policy_url="https://example.com/privacy",
        logo_path="/static/uploads/existing_logo.png"
    )
    db_session.add(customization)
    db_session.commit()
    
    # Set colors should update the existing record
    primary = "#111111"
    secondary = "#222222"
    result = set_colors(db_session, primary, secondary)
    
    # Verify the result
    assert result is not None
    assert result.primary_color == primary
    assert result.secondary_color == secondary
    assert result.company_name == "Test Company"  # Other fields should be preserved
    assert result.logo_path == "/static/uploads/existing_logo.png"  # Other fields should be preserved
    
    # Verify in database
    db_customization = db_session.query(Customization).first()
    assert db_customization is not None
    assert db_customization.primary_color == primary
    assert db_customization.secondary_color == secondary
    assert db_customization.company_name == "Test Company"  # Other fields should be preserved
    assert db_customization.logo_path == "/static/uploads/existing_logo.png"  # Other fields should be preserved
    
    # Clean up
    db_session.delete(db_customization)
    db_session.commit()
