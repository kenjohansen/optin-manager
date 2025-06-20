"""
api/customization.py

API endpoints for UI customization and branding settings.

This module provides endpoints for managing the application's branding and UI
customization, including logo uploads, color scheme settings, and communication
provider configurations. These settings allow organizations to personalize the
OptIn Manager interface to match their brand identity.

As noted in the memories, this supports UI branding elements and communication
provider settings that are essential for consistent user experience.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

import os
import logging
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Request
from app.api import provider_secrets
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_admin_user
from app.models.customization import Customization
from app.schemas.customization import CustomizationOut, CustomizationColorsUpdate
from starlette.responses import FileResponse

router = APIRouter(prefix="/customization", tags=["customization"])

# Set up logging
logger = logging.getLogger(__name__)

# Define upload directory using backend/static (MATCH FastAPI static mount)
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

logger.info(f"STATIC_DIR: {STATIC_DIR}")
logger.info(f"UPLOAD_DIR: {UPLOAD_DIR}")

# --- Accept POST on both /customization and /customization/ to avoid trailing slash issues ---
@router.post("", response_model=CustomizationOut, dependencies=[Depends(require_admin_user)])
@router.post("/", response_model=CustomizationOut, dependencies=[Depends(require_admin_user)])
async def save_customization(
    logo: UploadFile = File(None),
    primary: str = Form(None),
    secondary: str = Form(None),
    company_name: str = Form(None),
    privacy_policy_url: str = Form(None),
    email_provider: str = Form(None),
    sms_provider: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Save or update customization settings.
    
    This endpoint allows administrators to configure the branding and communication
    settings for the OptIn Manager application. It handles both the visual elements
    (company name, colors, logo) and the communication provider settings.
    
    The customization settings are essential for maintaining a consistent brand
    identity across all user-facing interfaces and for ensuring that communications
    are sent through the properly configured channels.
    
    The endpoint supports file uploads for the organization logo and stores it in
    a dedicated uploads directory with appropriate permissions. It also verifies
    file types to ensure only valid image formats are accepted.
    
    Args:
        logo (UploadFile, optional): Organization logo image file
        primary (str, optional): Primary brand color in hex format
        secondary (str, optional): Secondary brand color in hex format
        company_name (str, optional): Organization name for branding
        privacy_policy_url (str, optional): URL to the organization's privacy policy
        email_provider (str, optional): Email service provider name
        sms_provider (str, optional): SMS service provider name
        db (Session): SQLAlchemy database session
        
    Returns:
        CustomizationOut: The updated customization settings
        
    Requires:
        Admin role: Only administrators can modify customization settings
    """
    logger.info(f"save_customization called with logo: {logo is not None}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization()
        db.add(customization)
        logger.info("Created new customization record")
    else:
        logger.info(f"Using existing customization record with ID: {customization.id}")
    
    if logo is not None:
        try:
            logger.info(f"Processing logo upload: {logo.filename}")
            ext = os.path.splitext(logo.filename)[-1].lower()
            if ext not in [".png", ".jpg", ".jpeg", ".svg"]:
                logger.error(f"Invalid file type: {ext}")
                raise HTTPException(status_code=400, detail="Invalid file type.")
            
            filename = f"logo{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            logger.info(f"[UPLOAD DEBUG] Attempting to save logo to: {filepath}")
            logger.info(f"[UPLOAD DEBUG] UPLOAD_DIR: {UPLOAD_DIR}")
            logger.info(f"[UPLOAD DEBUG] STATIC_DIR: {STATIC_DIR}")
            try:
                contents = logo.file.read()
                logger.info(f"[UPLOAD DEBUG] Read {len(contents)} bytes from uploaded file")
                with open(filepath, "wb") as f:
                    f.write(contents)
                logger.info(f"[UPLOAD DEBUG] Successfully wrote logo to {filepath}")
            except Exception as file_write_err:
                logger.error(f"[UPLOAD DEBUG] Error writing logo file: {file_write_err}")
                raise HTTPException(status_code=500, detail=f"Error writing logo file: {file_write_err}")
            
            # Verify the file was saved
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Verified file exists with size: {file_size} bytes")
                # Force permissions to ensure it's readable
                os.chmod(filepath, 0o644)
                logger.info(f"Set permissions on {filepath} to 644")
            else:
                logger.error(f"File was not saved at {filepath}")
                raise HTTPException(status_code=500, detail="Failed to save logo file")
            
            # Update database record - store just the filename
            customization.logo_path = filename
            logger.info(f"Updated customization.logo_path to {filename}")
        except Exception as e:
            logger.exception(f"Error processing logo upload: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing logo upload: {str(e)}")
    
    if primary is not None:
        customization.primary_color = primary
    if secondary is not None:
        customization.secondary_color = secondary
    if company_name is not None:
        customization.company_name = company_name
    if privacy_policy_url is not None:
        customization.privacy_policy_url = privacy_policy_url
    if email_provider is not None:
        customization.email_provider = email_provider
    if sms_provider is not None:
        customization.sms_provider = sms_provider
    
    db.commit()
    logger.info("Committed customization changes to database")
    
    logo_url = f"/static/uploads/{customization.logo_path}" if customization.logo_path else None
    logger.info(f"Returning logo_url: {logo_url}")
    
    return CustomizationOut(
        logo_url=logo_url,
        primary_color=customization.primary_color,
        secondary_color=customization.secondary_color,
        company_name=customization.company_name,
        privacy_policy_url=customization.privacy_policy_url,
        email_provider=customization.email_provider,
        sms_provider=customization.sms_provider,
        email_connection_status=getattr(customization, 'email_connection_status', None),
        sms_connection_status=getattr(customization, 'sms_connection_status', None)
    )

@router.get("", response_model=CustomizationOut)
@router.get("/", response_model=CustomizationOut)
def get_customization(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve current customization settings.
    
    This endpoint provides the current branding and communication settings for
    the application. It's used by the frontend to apply the correct visual styling
    and to display organization-specific information.
    
    Unlike other endpoints, this one does not require authentication since the
    branding needs to be visible to all users, including those who are not logged in.
    This allows the login page and public-facing components to display the correct
    branding.
    
    Args:
        request (Request): FastAPI request object
        db (Session): SQLAlchemy database session
        
    Returns:
        CustomizationOut: The current customization settings
    """
    customization = db.query(Customization).first()
    if not customization:
        return CustomizationOut(
            logo_url=None,
            primary_color=None,
            secondary_color=None,
            company_name=None,
            privacy_policy_url=None,
            email_provider=None,
            sms_provider=None,
            email_connection_status=None,
            sms_connection_status=None
        )
    logo_url = None
    if customization.logo_path:
        # Return just the path without the domain - frontend will handle adding the domain
        logo_url = f"/static/uploads/{customization.logo_path}"
        logger.info(f"get_customization returning logo_url: {logo_url}")
        
        # Verify the file exists
        filepath = os.path.join(UPLOAD_DIR, customization.logo_path)
        if not os.path.exists(filepath):
            logger.warning(f"Logo file does not exist at {filepath}")
    
    return CustomizationOut(
        logo_url=logo_url,
        primary_color=customization.primary_color,
        secondary_color=customization.secondary_color,
        company_name=customization.company_name,
        privacy_policy_url=customization.privacy_policy_url,
        email_provider=customization.email_provider,
        sms_provider=customization.sms_provider,
        email_connection_status=getattr(customization, 'email_connection_status', None),
        sms_connection_status=getattr(customization, 'sms_connection_status', None)
    )


@router.post("/logo", response_model=CustomizationOut, dependencies=[Depends(require_admin_user)])
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logger.info(f"upload_logo called with file: {file.filename}")
    
    try:
        ext = os.path.splitext(file.filename)[-1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".svg"]:
            logger.error(f"Invalid file type: {ext}")
            raise HTTPException(status_code=400, detail="Invalid file type.")
        
        filename = f"logo{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        logger.info(f"Saving logo to: {filepath}")
        
        # DIRECT APPROACH: Use a simple file write operation
        contents = file.file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        
        logger.info(f"Logo saved successfully to {filepath}")
        
        # Verify the file was saved
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            logger.info(f"Verified file exists with size: {file_size} bytes")
            
            # Force permissions to ensure it's readable
            os.chmod(filepath, 0o644)
            logger.info(f"Set permissions on {filepath} to 644")
        else:
            logger.error(f"File was not saved at {filepath}")
            raise HTTPException(status_code=500, detail="Failed to save logo file")
        
        customization = db.query(Customization).first()
        if not customization:
            customization = Customization(logo_path=filename)
            db.add(customization)
            logger.info("Created new customization record")
        else:
            customization.logo_path = filename
            logger.info(f"Updated existing customization record with logo_path: {filename}")
        
        db.commit()
        logger.info("Committed customization changes to database")
        
        logo_url = f"/static/uploads/{filename}"
        logger.info(f"Returning logo_url: {logo_url}")
        
        return CustomizationOut(
            logo_url=logo_url,
            primary_color=customization.primary_color,
            secondary_color=customization.secondary_color
        )
    except Exception as e:
        logger.exception(f"Error in upload_logo: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")

@router.put("/colors", response_model=CustomizationOut, dependencies=[Depends(require_admin_user)])
def update_colors(
    payload: CustomizationColorsUpdate,
    db: Session = Depends(get_db),
):
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization(primary_color=payload.primary_color, secondary_color=payload.secondary_color)
        db.add(customization)
    else:
        customization.primary_color = payload.primary_color
        customization.secondary_color = payload.secondary_color
    db.commit()
    # Return just the path, not including the domain
    logo_url = f"/static/uploads/{customization.logo_path}" if customization.logo_path else None
    return CustomizationOut(
        logo_url=logo_url,
        primary_color=customization.primary_color,
        secondary_color=customization.secondary_color
    )
