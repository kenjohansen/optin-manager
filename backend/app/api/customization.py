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

# Define upload directory using absolute paths to ensure consistency
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

logger.info(f"BASE_DIR: {BASE_DIR}")
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
            
            logger.info(f"Saving logo to: {filepath}")
            
            # DIRECT APPROACH: Use a simple file write operation
            contents = logo.file.read()
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

@router.get("/", response_model=CustomizationOut)
def get_customization(request: Request, db: Session = Depends(get_db)):
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
