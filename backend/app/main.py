from fastapi import FastAPI
from .core.config import settings
from fastapi import FastAPI
from app.api import consent, message, message_template, campaign, verification_code, auth, auth_user, contact, customization

# --- DEV ONLY: Drop and recreate all tables on startup (remove when Alembic is reinstated) ---
from app.core.database import Base, engine
from app.models import user as user_model, campaign as campaign_model, message as message_model, message_template as message_template_model, verification_code as verification_code_model  # Only for table creation, not routers
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
# -------------------------------------------------------------------------------------------

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="OptIn Manager API")

# Serve static files for logo uploads
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_user.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(consent.router, prefix="/api/v1")
app.include_router(message.router, prefix="/api/v1")
app.include_router(message_template.router, prefix="/api/v1")
app.include_router(campaign.router, prefix="/api/v1")
app.include_router(verification_code.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(customization.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
