"""
schemas/customization.py

Pydantic schemas for UI and provider customization in the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from pydantic import BaseModel
from typing import Optional

class CustomizationOut(BaseModel):
    """
    Schema for returning customization settings via API.
    
    This schema contains both UI customization settings (logo, colors, company name)
    and provider configuration information (email/SMS providers and connection status).
    These settings allow organizations to brand the OptIn Manager with their own
    identity and configure communication providers according to their needs.
    
    As noted in the memories, the Customization page is modular with separate
    components for Branding and Provider sections, and the UI persists settings
    between sessions without needing to reset the database.
    """
    logo_url: Optional[str]  # URL to the organization's logo image
    primary_color: Optional[str]  # Primary brand color (hex code)
    secondary_color: Optional[str]  # Secondary brand color (hex code)
    company_name: Optional[str]  # Organization name for display
    privacy_policy_url: Optional[str]  # URL to the organization's privacy policy
    email_provider: Optional[str]  # Selected email service provider
    sms_provider: Optional[str]  # Selected SMS service provider
    email_connection_status: Optional[str]  # Connection status for email provider
    sms_connection_status: Optional[str]  # Connection status for SMS provider

    model_config = {"from_attributes": True}  # Enable ORM model -> Pydantic conversion

class CustomizationColorsUpdate(BaseModel):
    """
    Schema for updating just the color settings.
    
    This focused schema allows updating only the color settings without affecting
    other customization parameters. This granular approach to updates supports the
    modular UI design noted in the memories, where different aspects of customization
    can be managed independently.
    
    The primary and secondary colors are required fields to ensure a complete and
    consistent color scheme update.
    """
    primary_color: str  # New primary brand color (hex code)
    secondary_color: str  # New secondary brand color (hex code)
