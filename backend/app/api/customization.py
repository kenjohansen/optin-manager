import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from app.api import provider_secrets
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_admin_user
from app.models.customization import Customization
from app.schemas.customization import CustomizationOut, CustomizationColorsUpdate
from starlette.responses import FileResponse

router = APIRouter(prefix="/customization", tags=["customization"])

UPLOAD_DIR = os.getenv("CUSTOMIZATION_UPLOAD_DIR", "static/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Accept POST on both /customization and /customization/ to avoid trailing slash issues ---
@router.post("", response_model=CustomizationOut, dependencies=[Depends(require_admin_user)])
@router.post("/", response_model=CustomizationOut, dependencies=[Depends(require_admin_user)])
def save_customization(
    logo: UploadFile = File(None),
    primary: str = Form(None),
    secondary: str = Form(None),
    company_name: str = Form(None),
    privacy_policy_url: str = Form(None),
    email_provider: str = Form(None),
    sms_provider: str = Form(None),
    db: Session = Depends(get_db)
):
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization()
        db.add(customization)
    if logo is not None:
        ext = os.path.splitext(logo.filename)[-1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".svg"]:
            raise HTTPException(status_code=400, detail="Invalid file type.")
        filename = f"logo{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(logo.file.read())
        customization.logo_path = filepath
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
    logo_url = f"/static/uploads/{os.path.basename(customization.logo_path)}" if customization.logo_path else None
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
# --- End fix for trailing slash POST issue ---

from fastapi import Request

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
        base_url = str(request.base_url).rstrip("/")
        logo_url = f"{base_url}/static/uploads/{os.path.basename(customization.logo_path)}"
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
def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".svg"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    filename = f"logo{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization(logo_path=filepath)
        db.add(customization)
    else:
        customization.logo_path = filepath
    db.commit()
    logo_url = f"/static/uploads/{filename}"
    return CustomizationOut(
        logo_url=logo_url,
        primary_color=customization.primary_color,
        secondary_color=customization.secondary_color
    )

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
    logo_url = f"/static/uploads/{os.path.basename(customization.logo_path)}" if customization.logo_path else None
    return CustomizationOut(
        logo_url=logo_url,
        primary_color=customization.primary_color,
        secondary_color=customization.secondary_color
    )
