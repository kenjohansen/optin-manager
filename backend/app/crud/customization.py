from sqlalchemy.orm import Session
from app.models.customization import Customization
from typing import Optional

def get_customization(db: Session) -> Optional[Customization]:
    return db.query(Customization).first()

def set_logo_path(db: Session, path: str) -> Customization:
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization(logo_path=path)
        db.add(customization)
    else:
        customization.logo_path = path
    db.commit()
    return customization

def set_colors(db: Session, primary: str, secondary: str) -> Customization:
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization(primary_color=primary, secondary_color=secondary)
        db.add(customization)
    else:
        customization.primary_color = primary
        customization.secondary_color = secondary
    db.commit()
    return customization
