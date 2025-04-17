import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_admin_user
from app.models.customization import Customization
from app.schemas.customization import CustomizationOut, CustomizationColorsUpdate
from starlette.responses import FileResponse

router = APIRouter(prefix="/customization", tags=["customization"])

UPLOAD_DIR = os.getenv("CUSTOMIZATION_UPLOAD_DIR", "static/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=CustomizationOut)
def get_customization(db: Session = Depends(get_db)):
    customization = db.query(Customization).first()
    if not customization:
        return CustomizationOut(logo_url=None, primary_color=None, secondary_color=None)
    logo_url = f"/static/uploads/{os.path.basename(customization.logo_path)}" if customization.logo_path else None
    return CustomizationOut(
        logo_url=logo_url,
        primary_color=customization.primary_color,
        secondary_color=customization.secondary_color
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
