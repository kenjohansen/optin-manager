"""
api/preferences.py

Preferences (opt-out/in) API endpoints for the OptIn Manager backend.
Implements Phase 1: send/verify code, fetch/update preferences for a contact.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.contact import Contact
from app.models.optin import OptIn
from app.models.consent import Consent, ConsentStatusEnum
from app.models.verification_code import VerificationCode, VerificationPurposeEnum, VerificationStatusEnum
from app.schemas.contact import ContactOut
from app.core.database import get_db
from app.core.auth import create_access_token, oauth2_scheme
from jose import jwt, JWTError
from datetime import datetime, timedelta
import uuid, os, logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/preferences", tags=["preferences"])

# Custom dependency to make the token optional
# Security utilities
from fastapi import Header, Depends, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param

# Custom OAuth2 scheme that makes the token optional
class OptionalBearerAuth(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request):
        try:
            # Try to get the token using the parent class
            return await super().__call__(request)
        except HTTPException:
            # If no token or invalid token format, return None instead of raising an exception
            return None

# Create an instance of our custom scheme
optional_bearer = OptionalBearerAuth(auto_error=False)

# --- Helper: Find or create contact by email/phone ---
def get_or_create_contact(db: Session, contact: str):
    if "@" in contact:
        # Email contact
        db_contact = db.query(Contact).filter(Contact.email == contact).first()
        if not db_contact:
            db_contact = Contact(email=contact)
            db.add(db_contact)
            db.commit()
            db.refresh(db_contact)
    else:
        # Phone contact
        db_contact = db.query(Contact).filter(Contact.phone == contact).first()
        if not db_contact:
            db_contact = Contact(phone=contact)
            db.add(db_contact)
            db.commit()
            db.refresh(db_contact)
    return db_contact

# --- 1. Send Verification Code ---
@router.post("/send-code")
def send_code(payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        # Print the entire payload for debugging
        logger.info(f"Received payload: {payload}")
        
        # Extract and validate contact information
        try:
            contact_val = payload.get("contact")
            if not contact_val:
                raise HTTPException(status_code=400, detail="Missing contact information")
                
            # Log with masked contact info for privacy
            try:
                masked_contact = contact_val[:3] + "..." if contact_val else ""
                logger.info(f"Sending verification code to contact: {masked_contact}")
            except Exception as e:
                logger.error(f"Error masking contact: {str(e)}")
                
            db_contact = get_or_create_contact(db, contact_val)
            
            # Generate verification code
            code = str(uuid.uuid4())[:6]
            expires_at = datetime.utcnow() + timedelta(minutes=15)  # Extended to 15 minutes for better UX
            
            # Determine the purpose of the verification
            purpose_val = payload.get("purpose", "self_service")
            logger.info(f"Verification purpose: {purpose_val}")
            # Use the appropriate enum value from VerificationPurposeEnum
            # The enum only has opt_in, opt_out, and preference_change values
            if purpose_val == "verbal_auth":
                purpose_enum = VerificationPurposeEnum.opt_in  # Use opt_in for verbal authorization
            else:
                purpose_enum = VerificationPurposeEnum.opt_out  # Default to opt_out for self-service
        except Exception as e:
            logger.error(f"Error in initial processing: {str(e)}")
            raise
        
        try:
            # Create verification code record
            logger.info("Creating verification code record")
            db_code = VerificationCode(
                user_id=db_contact.id,
                code=code,
                channel="email" if "@" in contact_val else "sms",
                sent_to=contact_val,
                expires_at=expires_at,
                purpose=purpose_enum,
                status=VerificationStatusEnum.pending
            )
            db.add(db_code)
            db.commit()
            logger.info("Verification code record created successfully")
            
            # Load dependencies for sending the code
            logger.info("Loading dependencies for sending the code")
            from app.utils.send_code import CodeSender
            from app.core.provider_vault import ProviderSecretsVault
            from app.models.customization import Customization

            # Get customization settings
            logger.info("Getting customization settings")
            customization = db.query(Customization).first()
            company_name = customization.company_name if customization and customization.company_name else "Your Company"
            email_provider = customization.email_provider if customization and customization.email_provider else "aws_ses"
            sms_provider = customization.sms_provider if customization and customization.sms_provider else "aws_sns"
            logger.info(f"Customization settings: company_name={company_name}, email_provider={email_provider}, sms_provider={sms_provider}")
        except Exception as e:
            logger.error(f"Error in database operations: {str(e)}")
            raise
        
        try:
            # Get provider credentials
            logger.info("Getting provider credentials")
            vault = ProviderSecretsVault()
            email_creds = {
                "access_key": vault.get_secret("EMAIL_ACCESS_KEY"),
                "secret_key": vault.get_secret("EMAIL_SECRET_KEY"),
                "region": vault.get_secret("EMAIL_REGION") or "us-east-1",
                "from_address": vault.get_secret("EMAIL_FROM_ADDRESS") or os.getenv("SES_FROM_EMAIL") or "no-reply@example.com",
            }
            sms_creds = {
                "access_key": vault.get_secret("SMS_ACCESS_KEY"),
                "secret_key": vault.get_secret("SMS_SECRET_KEY"),
                "region": vault.get_secret("SMS_REGION") or "us-east-1",
            }
            logger.info("Provider credentials retrieved successfully")
            
            # Initialize code sender
            logger.info("Initializing code sender")
            sender = CodeSender(email_provider, sms_provider, email_creds, sms_creds)
            logger.info("Code sender initialized successfully")
        except Exception as e:
            logger.error(f"Error in provider credentials: {str(e)}")
            raise

        try:
            # Determine template based on purpose
            logger.info("Determining template based on purpose")
            purpose = payload.get("purpose", "self_service")
            auth_user_name = payload.get("auth_user_name")
            channel = "email" if "@" in contact_val else "SMS"
            logger.info(f"Template parameters: purpose={purpose}, auth_user_name={auth_user_name}, channel={channel}")
            
            # Get or construct the preferences URL
            logger.info("Getting preferences URL")
            preferences_url = payload.get("preferences_url")
            if not preferences_url:
                frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
                preferences_url = f"{frontend_url}/preferences?contact={contact_val}"
            logger.info(f"Preferences URL: {preferences_url}")
                
            # Create appropriate email/SMS template based on purpose
            logger.info("Creating email/SMS template")
            url = preferences_url
            if purpose == "verbal_auth" and auth_user_name:
                # Verbal Auth template (Double Opt-In)
                subject = f"Your {company_name} Preferences Verification Code"
                body = f"""Hello from {company_name} Compliant Optin Manager!\n\n{auth_user_name} has submitted your verbal authorization to opt in to receive notifications from our products and services.\n\nIf you wish to update or confirm your preferences, please visit this site and enter this code.\n\n{url}\nCode: {code}\n\nThanks!\n\nThe Compliance team at {company_name}"""
            else:
                # Self-service template
                subject = f"Your {company_name} Preferences Verification Code"
                body = f"""Hello from {company_name} Compliant Optin Manager!\n\nSomeone, hopefully you, has entered a request to change your {channel} preferences to receive notifications from our products or services.\n\nIf you wish to update or confirm your preferences, please visit this site and enter this code.\n\n{url}\nCode: {code}\n\nThanks!\n\nThe Compliance team at {company_name}"""
            logger.info("Email/SMS template created successfully")
        except Exception as e:
            logger.error(f"Error in template creation: {str(e)}")
            raise

        try:
            # Send the verification code
            logger.info("Sending verification code")
            sent_ok = False
            if "@" in contact_val:
                logger.info("Sending email verification code")
                sent_ok = sender.send_email_code(contact_val, code, subject=subject, body=body)
                masked_contact = contact_val[:3] + "..." if contact_val else ""
                logger.info(f"Email verification code sent to {masked_contact}: {sent_ok}")
            else:
                logger.info("Sending SMS verification code")
                sent_ok = sender.send_sms_code(contact_val, code, body=body)
                masked_contact = contact_val[:3] + "..." if contact_val else ""
                logger.info(f"SMS verification code sent to {masked_contact}: {sent_ok}")
                
            if not sent_ok:
                masked_contact = contact_val[:3] + "..." if contact_val else ""
                logger.error(f"Failed to send verification code to {masked_contact}")
                raise HTTPException(status_code=500, detail="Failed to send verification code. Please try again later.")
                
            # Return success response (only include code in non-prod environments)
            logger.info("Returning success response")
            return {
                "ok": True, 
                "code": code if os.getenv("ENV") != "prod" else None,
                "expires_in_minutes": 15
            }
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in sending verification code: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while sending the verification code")
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return a generic error message
        logger.error(f"Error in send_code: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while sending the verification code")

# --- 2. Verify Code ---
@router.post("/verify-code")
def verify_code(payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        # Extract and validate required parameters
        contact_val = payload.get("contact")
        code = payload.get("code")
        
        if not contact_val or not code:
            raise HTTPException(status_code=400, detail="Missing contact or verification code")
            
        masked_contact = contact_val[:3] + "..." if contact_val else ""
        logger.info(f"Verifying code for contact: {masked_contact}")
        
        # Get or create the contact
        db_contact = get_or_create_contact(db, contact_val)
        
        # Find the verification code in the database
        db_code = db.query(VerificationCode).filter(
            VerificationCode.user_id == db_contact.id,
            VerificationCode.code == code,
            VerificationCode.status == VerificationStatusEnum.pending,
            VerificationCode.expires_at > datetime.utcnow()
        ).first()
        
        # Check if code is valid
        if not db_code:
            masked_contact = contact_val[:3] + "..." if contact_val else ""
            logger.warning(f"Invalid or expired verification code for contact: {masked_contact}")
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
            
        # Mark code as verified
        db_code.status = VerificationStatusEnum.verified
        db_code.verified_at = datetime.utcnow()
        db.commit()
        
        # Generate JWT token for preferences access
        # Include additional claims for better security and debugging
        token_data = {
            "sub": str(db_contact.id),
            "scope": "contact",
            "channel": db_code.channel,
            "contact_value": contact_val,
            "verified_at": db_code.verified_at.isoformat() if db_code.verified_at else None
        }
        
        access_token = create_access_token(data=token_data)
        masked_contact = contact_val[:3] + "..." if contact_val else ""
        logger.info(f"Verification successful for contact: {masked_contact}")
        
        # Return success response with token
        return {
            "ok": True, 
            "token": access_token,
            "contact": contact_val  # Include contact for convenience
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return a generic error message
        logger.error(f"Error in verify_code: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while verifying the code")

# --- 3. Get Preferences ---
# This endpoint supports two authentication methods:
# 1. JWT token in the Authorization header
# 2. Contact parameter in the query string (for email links)
@router.get("/user-preferences", name="get_user_preferences")
def get_preferences(
    contact: str = Query(None, description="Contact email or phone for direct access"),
    auth: HTTPAuthorizationCredentials = Depends(optional_bearer),
    db: Session = Depends(get_db)
):
    try:
        logger.info("Fetching preferences")
        
        # Track authentication method for logging
        auth_method = None
        contact_id = None
        
        # Method 1: Contact parameter in query string (for direct links from email)
        if contact:
            auth_method = "contact_param"
            logger.info(f"Using contact parameter: {contact[:3]}...")
            
            # Find the contact by email or phone
            if "@" in contact:
                db_contact = db.query(Contact).filter(Contact.email == contact).first()
            else:
                db_contact = db.query(Contact).filter(Contact.phone == contact).first()
            
            if not db_contact:
                logger.warning(f"Contact not found: {contact[:3]}...")
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact_id = str(db_contact.id)
            logger.info(f"Found contact ID {contact_id} using contact parameter")
        
        # Method 2: JWT token in Authorization header
        elif auth and auth.credentials:
            auth_method = "jwt_token"
            token = auth.credentials
            logger.info(f"Using JWT token: {token[:10] if token else 'None'}...")
            
            # Validate JWT and extract contact_id
            try:
                # Use the same secret key that was used to create the token
                secret_key = os.getenv("SECRET_KEY", "changeme")
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                logger.debug(f"JWT payload: {payload}")
                
                contact_id = payload.get("sub")
                if not contact_id:
                    logger.warning(f"Token missing 'sub' claim: {payload}")
                    raise HTTPException(status_code=401, detail="Invalid token: missing contact ID")
                    
                logger.info(f"Found contact ID {contact_id} using JWT token")
            except JWTError as e:
                logger.error(f"JWT decode error: {str(e)}")
                raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        
        # If neither contact nor token is provided, return an error
        else:
            logger.warning("No authentication method provided")
            raise HTTPException(
                status_code=400, 
                detail="Either contact parameter or authorization token must be provided"
            )
        
        # At this point, we have a valid contact_id from either authentication method
        # Convert string UUID to UUID object if needed
        try:
            if isinstance(contact_id, str):
                contact_id = uuid.UUID(contact_id)
                logger.info(f"Converted string contact_id to UUID: {contact_id}")
        except ValueError as e:
            logger.error(f"Invalid UUID format: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid contact ID format")
            
        db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not db_contact:
            logger.warning(f"Contact with ID {contact_id} not found in database")
            raise HTTPException(status_code=404, detail="Contact not found")
            
        # Get all available opt-in campaigns
        optins = db.query(OptIn).all()
        
        # Get the user's existing consent records
        consents = {c.optin_id: c for c in db.query(Consent).filter(Consent.user_id == contact_id).all()}
        
        # Build the response with program information and opt-in status
        programs = []
        for optin in optins:
            consent = consents.get(optin.id)
            # Default to opted-in if no consent record exists
            opted_in = consent.status != ConsentStatusEnum.opt_out if consent else True
            
            programs.append({
                "id": str(optin.id), 
                "name": optin.name, 
                "description": optin.description,
                "opted_in": opted_in,
                "last_updated": consent.updated_at.isoformat() if consent and consent.updated_at else None
            })
            
        # Return the preferences data
        logger.info(f"Successfully fetched preferences for contact ID {contact_id} using {auth_method}")
        return {
            "contact": {
                "id": str(db_contact.id),
                "email": db_contact.email,
                "phone": db_contact.phone,
                "created_at": db_contact.created_at.isoformat() if db_contact.created_at else None,
                "comment": db_contact.comment
            },
            "global_opt_out": False,  # TODO: Implement global opt-out flag
            "programs": programs
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return a generic error message
        logger.error(f"Error in get_preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching preferences")

# --- 4. Update Preferences ---
@router.patch("/user-preferences", name="update_user_preferences")
def update_preferences(
    payload: dict = Body(...),
    contact: str = Query(None, description="Contact email or phone for direct access"),
    auth: HTTPAuthorizationCredentials = Depends(optional_bearer),
    db: Session = Depends(get_db)
):
    try:
        # Similar authentication as get_preferences
        auth_method = None
        contact_id = None
        
        # Method 1: Contact parameter in query string
        if contact:
            auth_method = "contact_param"
            if "@" in contact:
                db_contact = db.query(Contact).filter(Contact.email == contact).first()
            else:
                db_contact = db.query(Contact).filter(Contact.phone == contact).first()
            
            if not db_contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact_id = db_contact.id
        
        # Method 2: JWT token in Authorization header
        elif auth and auth.credentials:
            auth_method = "jwt_token"
            token = auth.credentials
            
            try:
                secret_key = os.getenv("SECRET_KEY", "changeme")
                payload_jwt = jwt.decode(token, secret_key, algorithms=["HS256"])
                
                contact_id_str = payload_jwt.get("sub")
                if not contact_id_str:
                    raise HTTPException(status_code=401, detail="Invalid token: missing contact ID")
                
                # Convert string UUID to UUID object
                try:
                    contact_id = uuid.UUID(contact_id_str)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid contact ID format in token")
                
            except JWTError as e:
                raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        
        # If neither contact nor token is provided, return an error
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either contact parameter or authorization token must be provided"
            )
        
        # At this point, we have a valid contact_id from either authentication method
        db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not db_contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Handle global opt-out flag if present
        global_opt_out = payload.get("global_opt_out")
        if global_opt_out is not None:
            # TODO: Implement global opt-out flag
            pass
        
        # Handle comment if present
        comment = payload.get("comment")
        if comment is not None:
            db_contact.comment = comment
            db.commit()
        
        # Handle program-specific opt-in/out
        # Extract program preferences from payload
        programs = {}
        for key, value in payload.items():
            if key.startswith("program_"):
                program_id = key.replace("program_", "")
                programs[program_id] = value
        
        # Update consent records for each program
        for program_id, opted_in in programs.items():
            try:
                # Convert string UUID to UUID object
                optin_id = uuid.UUID(program_id)
                
                # Verify the program exists
                optin = db.query(OptIn).filter(OptIn.id == optin_id).first()
                if not optin:
                    continue  # Skip invalid program IDs
                
                # Find existing consent record or create new one
                consent = db.query(Consent).filter(
                    Consent.user_id == contact_id,
                    Consent.optin_id == optin_id
                ).first()
                
                if consent:
                    # Update existing consent
                    consent.status = ConsentStatusEnum.opt_in if opted_in else ConsentStatusEnum.opt_out
                    consent.updated_at = datetime.utcnow()
                else:
                    # Create new consent record
                    consent = Consent(
                        user_id=contact_id,
                        optin_id=optin_id,
                        status=ConsentStatusEnum.opt_in if opted_in else ConsentStatusEnum.opt_out,
                        updated_at=datetime.utcnow()
                    )
                    db.add(consent)
                
                db.commit()
                
            except ValueError:
                # Skip invalid UUIDs
                continue
        
        # Return updated preferences
        return {
            "ok": True,
            "message": "Preferences updated successfully"
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return a generic error message
        logger.error(f"Error in update_preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating preferences")
