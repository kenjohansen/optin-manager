from fastapi import FastAPI
from .core.config import settings
from fastapi import FastAPI
from app.api import consent, message, message_template, campaign, verification_code, auth, auth_user, contact, customization, preferences, provider_secrets


from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.models.auth_user import AuthUser
from app.crud.auth_user import pwd_context
from sqlalchemy import select
import uuid

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OptIn Manager API")

# Enable CORS for frontend
# --- CORS Middleware ---
# For development, allow all origins to avoid CORS issues with changing frontend ports.
# IMPORTANT: In production, restrict 'allow_origins' to trusted frontend URLs only for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Ensure all tables exist and default admin user exists on startup ---
from sqlalchemy import inspect
from app.core.database import engine, Base

def ensure_tables_and_admin():
    inspector = inspect(engine)
    # List of required tables (add more as your models grow)
    required_tables = ["auth_users"]
    existing_tables = inspector.get_table_names()
    if not all(table in existing_tables for table in required_tables):
        print("[INFO] Creating all tables from models (some required tables missing)...")
        Base.metadata.create_all(bind=engine)
    # Now ensure default admin
    from app.core.database import SessionLocal
    db: Session = SessionLocal()
    try:
        user_count = db.query(AuthUser).count()
        if user_count == 0:
            admin_user = AuthUser(
                id=uuid.uuid4(),
                username="admin",
                password_hash=pwd_context.hash("TestAdmin123"),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("[STARTUP] Default admin user created: admin / TestAdmin123 (please change this password on first login)")
        else:
            print(f"[STARTUP] Admin user(s) already exist in auth_users table: {user_count} user(s)")
    finally:
        db.close()


import subprocess
from sqlalchemy.engine import Engine

def print_db_and_alembic_info(engine: Engine):
    print(f"[STARTUP] SQLAlchemy DB URL: {engine.url}")
    try:
        alembic_version = subprocess.check_output([
            "alembic", "current", "--verbose"
        ], cwd=os.path.dirname(__file__) + '/../').decode().strip()
        print(f"[STARTUP] Alembic migration version:\n{alembic_version}")
    except Exception as e:
        print(f"[STARTUP] Alembic version check failed: {e}")

def auto_run_alembic_upgrade():
    import os
    import sys
    import subprocess
    db_url = str(engine.url)
    # Only run for SQLite/Postgres, not in-memory/test
    if db_url.startswith("sqlite") or db_url.startswith("postgresql"):
        print("[STARTUP] Running Alembic migrations (auto-upgrade)...")
        try:
            subprocess.run([
                sys.executable, "-m", "alembic", "upgrade", "head"
            ], cwd=os.path.dirname(os.path.dirname(__file__)), check=True)
            print("[STARTUP] Alembic migrations complete.")
        except Exception as e:
            print(f"[STARTUP][ERROR] Alembic migration failed: {e}")
            sys.exit(1)
    else:
        print("[STARTUP] Skipping Alembic migrations: unsupported DB URL.")

# Run Alembic migrations before anything else
auto_run_alembic_upgrade()
print_db_and_alembic_info(engine)
ensure_tables_and_admin()

# Serve static files for logo uploads
app.mount("/static", StaticFiles(directory="static"), name="static")

from app.api import dashboard
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(auth_user.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(consent.router, prefix="/api/v1")
app.include_router(message.router, prefix="/api/v1")
app.include_router(message_template.router, prefix="/api/v1")
app.include_router(campaign.router, prefix="/api/v1")
app.include_router(verification_code.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(customization.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")
app.include_router(provider_secrets.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
