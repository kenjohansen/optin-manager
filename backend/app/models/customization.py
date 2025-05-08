"""
models/customization.py

SQLAlchemy model for UI and provider customization settings in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Customization(Base):
    """
    SQLAlchemy model for UI and provider customization settings.
    
    The Customization model stores system-wide configuration settings for both
    UI branding elements and communication provider settings. This centralized
    approach allows administrators to manage all customization from a single
    interface, ensuring consistent branding across the application.
    
    As noted in the memories, the Customization page is fully modular with separate
    components for Branding and Provider sections. The UI persists settings between
    sessions, and the system supports testing connection credentials before saving.
    
    This model is designed to have only one active record at a time, as these are
    global settings for the entire application.
    """
    __tablename__ = "customization"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    """
    Unique identifier for the customization record. While typically only one record
    exists, using a UUID allows for potential future expansion to support multiple
    customization profiles.
    """
    
    # Branding elements
    logo_path = Column(String, nullable=True)
    """
    Path to the company logo image file. This is used throughout the UI to
    provide consistent branding and visual identity.
    """
    
    primary_color = Column(String, nullable=True)
    """
    Primary brand color in hex format (e.g., '#1976D2'). This color is used
    for primary UI elements like buttons and headers.
    """
    
    secondary_color = Column(String, nullable=True)
    """
    Secondary brand color in hex format (e.g., '#424242'). This color is used
    for secondary UI elements and accents.
    """
    
    company_name = Column(String, nullable=True)
    """
    Name of the company or organization. This appears in various places in the UI
    and in communication templates.
    """
    
    privacy_policy_url = Column(String, nullable=True)
    """
    URL to the organization's privacy policy. This is essential for regulatory
    compliance, as users must have access to privacy information when providing consent.
    """
    
    # Communication provider settings
    email_provider = Column(String, nullable=True)  # e.g., 'aws_ses', 'sendgrid', etc.
    """
    Selected email service provider (e.g., 'aws_ses', 'sendgrid'). This determines
    which email integration is used for sending verification codes and notifications.
    """
    
    sms_provider = Column(String, nullable=True)    # e.g., 'aws_sns', 'twilio', etc.
    """
    Selected SMS service provider (e.g., 'aws_sns', 'twilio'). This determines
    which SMS integration is used for sending verification codes and notifications.
    """
    
    email_connection_status = Column(String, nullable=True)  # 'untested', 'tested', 'failed'
    """
    Status of the email provider connection ('untested', 'tested', 'failed').
    This tracks whether the credentials have been successfully tested.
    """
    
    sms_connection_status = Column(String, nullable=True)    # 'untested', 'tested', 'failed'
    """
    Status of the SMS provider connection ('untested', 'tested', 'failed').
    This tracks whether the credentials have been successfully tested.
    """
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    """
    Timestamp of the last update to the customization settings. This is automatically
    updated whenever any field is modified, providing an audit trail of changes.
    """
