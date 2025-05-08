"""
crud/customization.py

CRUD operations for Customization model.

This module provides database operations for managing UI and provider customization
settings in the OptIn Manager system. These operations support the Customization page,
which is fully modular with separate components for Branding and Provider sections.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from sqlalchemy.orm import Session
from app.models.customization import Customization
from typing import Optional

def get_customization(db: Session) -> Optional[Customization]:
    """
    Retrieve the current customization settings.
    
    This function returns the single customization record that contains all branding
    and provider settings. The system is designed to have only one active customization
    record at a time, as these are global settings for the entire application.
    
    Args:
        db (Session): SQLAlchemy database session
        
    Returns:
        Optional[Customization]: The customization record if found, None otherwise
    """
    return db.query(Customization).first()

def set_logo_path(db: Session, path: str) -> Customization:
    """
    Set the logo path in the customization settings.
    
    This function updates or creates the customization record with the provided
    logo path. The logo is an important branding element that appears throughout
    the UI to provide consistent visual identity.
    
    Args:
        db (Session): SQLAlchemy database session
        path (str): Path to the logo image file
        
    Returns:
        Customization: The updated customization record
    """
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization(logo_path=path)
        db.add(customization)
    else:
        customization.logo_path = path
    db.commit()
    return customization

def set_colors(db: Session, primary: str, secondary: str) -> Customization:
    """
    Set the primary and secondary colors in the customization settings.
    
    This function updates or creates the customization record with the provided
    color values. These colors are used throughout the UI to maintain consistent
    branding, with the primary color used for main UI elements like buttons and
    headers, and the secondary color used for accents and secondary elements.
    
    Args:
        db (Session): SQLAlchemy database session
        primary (str): Primary brand color in hex format (e.g., '#1976D2')
        secondary (str): Secondary brand color in hex format (e.g., '#424242')
        
    Returns:
        Customization: The updated customization record
    """
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization(primary_color=primary, secondary_color=secondary)
        db.add(customization)
    else:
        customization.primary_color = primary
        customization.secondary_color = secondary
    db.commit()
    return customization
