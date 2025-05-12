"""
app/main.py

Main FastAPI application entry point for the OptIn Manager backend.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import FastAPI
from .core.config import settings
from fastapi import FastAPI
from app.api import consent, message, message_template, verification_code, auth, auth_user, contact, customization, preferences, provider_secrets, optin


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from sqlalchemy.orm import Session
from app.models.auth_user import AuthUser
from app.crud.auth_user import pwd_context
from sqlalchemy import select
import uuid

from fastapi.middleware.cors import CORSMiddleware

# Define the static directory and favicon paths to point to backend/static
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
FAVICON_PATH = os.path.join(STATIC_DIR, "favicon.ico")

# --- Ensure uploads directory exists on startup ---
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR, exist_ok=True)

# Create the FastAPI app with custom docs configuration
app = FastAPI(
    title="OptIn Manager API",
    description="API for managing opt-in preferences and communications",
    version="1.0.0",
    # Override the default FastAPI docs templates to use our custom favicon
    # This customization is important for branding consistency and to provide
    # a professional appearance for the API documentation
    swagger_ui_parameters={
        "persistAuthorization": True,  # Maintain auth token between page refreshes
        "favicon": "/static/favicon.ico",  # Direct parameter for Swagger UI
    },
    # These are used by FastAPI but sometimes don't work with all versions
    # We include multiple favicon settings to ensure compatibility across
    # different FastAPI versions and documentation UI implementations
    swagger_favicon_url="/static/favicon.ico",
    swagger_ui_favicon_url="/static/favicon.ico",
    redoc_favicon_url="/static/favicon.ico",
    docs_url=None,  # Disable default docs to use our custom route
    redoc_url=None  # Disable default redoc to use our custom route
)

# --- CORS Middleware ---
"""
Enable Cross-Origin Resource Sharing (CORS) for the frontend.

CORS is necessary to allow the frontend application to communicate with the API
when they are hosted on different domains or ports. This is particularly important
during development when the frontend and backend are typically running on different
ports on localhost.

For development, we allow all origins to avoid CORS issues with changing frontend ports.
IMPORTANT: In production, restrict 'allow_origins' to trusted frontend URLs only for security.
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],    # Allow all HTTP methods
    allow_headers=["*"],    # Allow all headers
)

# --- Request/Response Logging Middleware ---
import time
from starlette.middleware.base import BaseHTTPMiddleware
import json
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response details.
    
    This middleware provides detailed logging of all HTTP requests and responses,
    which is essential for debugging API issues, monitoring performance, and
    understanding how the API is being used. Each request is assigned a unique
    ID based on the timestamp to correlate request and response logs.
    
    The logs include request method, path, query parameters, headers, response
    status code, and processing time, providing a comprehensive view of the
    request lifecycle for troubleshooting.
    """
    async def dispatch(self, request, call_next):
        # Log request details
        request_id = str(time.time())
        print(f"\n[DEBUG-REQUEST-{request_id}] {request.method} {request.url.path}")
        print(f"[DEBUG-REQUEST-{request_id}] Query params: {dict(request.query_params)}")
        print(f"[DEBUG-REQUEST-{request_id}] Headers: {dict(request.headers)}")
        
        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        print(f"[DEBUG-RESPONSE-{request_id}] Status: {response.status_code}")
        print(f"[DEBUG-RESPONSE-{request_id}] Process time: {process_time:.4f} sec")
        
        return response

app.add_middleware(RequestLoggingMiddleware)

# --- Exception Handlers ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"\n[VALIDATION-ERROR] Request URL: {request.url}")
    print(f"[VALIDATION-ERROR] Request method: {request.method}")
    print(f"[VALIDATION-ERROR] Request headers: {dict(request.headers)}")
    print(f"[VALIDATION-ERROR] Error details: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# --- Ensure all tables exist and default admin user exists on startup ---
from sqlalchemy import inspect
from app.core.database import engine, Base

def ensure_tables_and_admin():
    """
    Ensure all required database tables exist and create a default admin user if needed.
    
    This function performs two critical startup tasks:
    1. Checks if required database tables exist and creates them if missing
    2. Creates a default admin user if no users exist in the system
    
    The default admin user is essential for first-time setup, allowing immediate
    access to the admin interface without requiring complex user creation steps.
    This simplifies deployment and initial configuration of the system.
    
    SECURITY NOTE: The default admin password should be changed immediately after
    first login in a production environment.
    """
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
                id=str(uuid.uuid4()),  # Convert UUID to string for SQLite compatibility
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
    import json
    db_url = str(engine.url)
    # Only run for SQLite/Postgres, not in-memory/test
    if db_url.startswith("sqlite") or db_url.startswith("postgresql"):
        print("[STARTUP] Running Alembic migrations (auto-upgrade)...")
        try:
            # For Phase 1, we'll check if the consents table exists first
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Backup customization data if it exists
            customization_data = None
            if 'customization' in tables:
                from app.core.database import SessionLocal
                from app.models.customization import Customization
                from sqlalchemy.orm import Session
                
                db: Session = SessionLocal()
                try:
                    customization = db.query(Customization).first()
                    if customization:
                        print("[STARTUP] Backing up customization data before migrations")
                        customization_data = {
                            "logo_path": customization.logo_path,
                            "primary_color": customization.primary_color,
                            "secondary_color": customization.secondary_color,
                            "company_name": customization.company_name,
                            "privacy_policy_url": customization.privacy_policy_url,
                            "email_provider": customization.email_provider,
                            "sms_provider": customization.sms_provider,
                            "email_connection_status": customization.email_connection_status,
                            "sms_connection_status": customization.sms_connection_status
                        }
                        # Save backup to file
                        backup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "customization_backup.json")
                        with open(backup_path, 'w') as f:
                            json.dump(customization_data, f)
                        print(f"[STARTUP] Customization data backed up to {backup_path}")
                finally:
                    db.close()
            
            if 'consents' in tables:
                print("[STARTUP] Consents table already exists, skipping migrations.")
                # Restore customization data if we have a backup
                if customization_data:
                    restore_customization(customization_data)
                return
                
            # Try to run migrations, but don't fail if they don't work
            result = subprocess.run([
                sys.executable, "-m", "alembic", "upgrade", "head"
            ], cwd=os.path.dirname(os.path.dirname(__file__)), check=False)
            
            if result.returncode == 0:
                print("[STARTUP] Alembic migrations complete.")
                # Restore customization data if we have a backup
                if customization_data:
                    restore_customization(customization_data)
            else:
                print(f"[STARTUP][WARNING] Alembic migrations had issues, but continuing anyway.")
                # Try to restore customization data anyway
                if customization_data:
                    restore_customization(customization_data)
        except Exception as e:
            print(f"[STARTUP][WARNING] Alembic migration error: {e}")
            print("[STARTUP] Continuing without migrations...")
            # Try to restore from backup file if it exists
            try:
                backup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "customization_backup.json")
                if os.path.exists(backup_path):
                    with open(backup_path, 'r') as f:
                        customization_data = json.load(f)
                    restore_customization(customization_data)
            except Exception as restore_error:
                print(f"[STARTUP][WARNING] Failed to restore customization data: {restore_error}")
    else:
        print("[STARTUP] Skipping Alembic migrations: unsupported DB URL.")

def restore_customization(customization_data):
    """Restore customization data from backup"""
    try:
        from app.core.database import SessionLocal
        from app.models.customization import Customization
        from sqlalchemy.orm import Session
        
        print("[STARTUP] Restoring customization data from backup")
        db: Session = SessionLocal()
        try:
            customization = db.query(Customization).first()
            if not customization:
                customization = Customization()
                db.add(customization)
            
            # Restore all fields
            for key, value in customization_data.items():
                if hasattr(customization, key):
                    setattr(customization, key, value)
            
            db.commit()
            print("[STARTUP] Customization data restored successfully")
        finally:
            db.close()
    except Exception as e:
        print(f"[STARTUP][WARNING] Error restoring customization data: {e}")
        print("[STARTUP] Continuing without restoring customization...")


# Run Alembic migrations before anything else
auto_run_alembic_upgrade()
print_db_and_alembic_info(engine)
ensure_tables_and_admin()

# Serve static files for logo uploads and favicon at /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Custom favicon endpoint
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Serve custom favicon with no-cache to force refresh
    return FileResponse(FAVICON_PATH, headers={"Cache-Control": "no-store, max-age=0"})

# Custom Swagger UI with our favicon
from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
    )

# Custom ReDoc with our favicon
from fastapi.openapi.docs import get_redoc_html

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico",
    )

from app.api import dashboard
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(auth_user.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(consent.router, prefix="/api/v1")
app.include_router(message.router, prefix="/api/v1")
app.include_router(message_template.router, prefix="/api/v1")
app.include_router(verification_code.router, prefix="/api/v1")
app.include_router(optin.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(customization.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")
app.include_router(provider_secrets.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
