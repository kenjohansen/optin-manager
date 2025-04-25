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

# Define the static directory and favicon paths
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
FAVICON_PATH = os.path.join(STATIC_DIR, "favicon.ico")

# Create the FastAPI app with custom docs configuration
app = FastAPI(
    title="OptIn Manager API",
    description="API for managing opt-in preferences and communications",
    version="1.0.0",
    # Override the default FastAPI docs templates to use our custom favicon
    swagger_ui_parameters={
        "persistAuthorization": True,
        "favicon": "/static/favicon.ico",  # Direct parameter for Swagger UI
    },
    # These are used by FastAPI but sometimes don't work with all versions
    swagger_favicon_url="/static/favicon.ico",
    swagger_ui_favicon_url="/static/favicon.ico",
    redoc_favicon_url="/static/favicon.ico",
    docs_url=None,  # Disable default docs to use our custom route
    redoc_url=None  # Disable default redoc to use our custom route
)

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

# --- Request/Response Logging Middleware ---
import time
from starlette.middleware.base import BaseHTTPMiddleware
import json
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class RequestLoggingMiddleware(BaseHTTPMiddleware):
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
            # For Phase 1, we'll check if the consents table exists first
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'consents' in tables:
                print("[STARTUP] Consents table already exists, skipping migrations.")
                return
                
            # Try to run migrations, but don't fail if they don't work
            result = subprocess.run([
                sys.executable, "-m", "alembic", "upgrade", "head"
            ], cwd=os.path.dirname(os.path.dirname(__file__)), check=False)
            
            if result.returncode == 0:
                print("[STARTUP] Alembic migrations complete.")
            else:
                print(f"[STARTUP][WARNING] Alembic migrations had issues, but continuing anyway.")
        except Exception as e:
            print(f"[STARTUP][WARNING] Alembic migration error: {e}")
            print("[STARTUP] Continuing without migrations...")
    else:
        print("[STARTUP] Skipping Alembic migrations: unsupported DB URL.")

# Run Alembic migrations before anything else
auto_run_alembic_upgrade()
print_db_and_alembic_info(engine)
ensure_tables_and_admin()

# Serve static files for logo uploads and favicon
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
