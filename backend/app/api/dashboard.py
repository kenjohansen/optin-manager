from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.auth_user import AuthUser
from app.models.optin import OptIn
from app.models.message import Message
from app.models.message_template import MessageTemplate

router = APIRouter()

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    users = db.query(AuthUser).count()
    optins = db.query(OptIn).count()
    messages = db.query(Message).count()
    templates = db.query(MessageTemplate).count()
    return {
        "users": users,
        "optins": optins,
        "messages": messages,
        "templates": templates,
    }
