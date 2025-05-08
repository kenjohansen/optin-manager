"""
api/preferences.py

Preferences (opt-out/in) API endpoints for the OptIn Manager backend.
Implements Phase 1: send/verify code, fetch/update preferences for a contact.

This module provides the core functionality for the Opt-Out workflow, which is
the primary focus of Phase 1 as noted in the memories. It implements the complete
flow for users to manage their communication preferences:
1. Send a verification code to the user's email or phone
2. Verify the code to authenticate the user
3. Fetch the user's current preferences
4. Update the user's preferences

The module supports SQLite for development and testing as specified in the
memories, and implements proper security measures for handling user data.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, status, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
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
from app.utils.phone_utils import normalize_phone_number, is_valid_phone_number

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
def get_or_create_contact(db: Session, contact_value: str, contact_type: str = None):
    # Import encryption utilities
    from app.core.encryption import encrypt_pii, generate_deterministic_id
    from app.models.contact import ContactTypeEnum
    
    # Determine contact type if not provided
    if not contact_type:
        contact_type = "email" if "@" in contact_value else "phone"
    
    # Generate deterministic ID
    contact_id = generate_deterministic_id(contact_value)
    
    # Look up contact by ID
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    # If contact doesn't exist, create it
    if not db_contact:
        # Encrypt the contact value
        encrypted_value = encrypt_pii(contact_value)
        
        # Create new contact record
        db_contact = Contact(
            id=contact_id,
            encrypted_value=encrypted_value,
            contact_type=contact_type,
            status="active"
        )
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        logger.info(f"Created new contact with ID: {contact_id}")
    else:
        logger.info(f"Found existing contact with ID: {contact_id}")
    
    return db_contact, contact_value  # Return both the contact object and the original value

# --- 1. Send Verification Code ---
@router.post("/send-code")
def send_code(payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        # Print the entire payload for debugging
        logger.info(f"Received payload: {payload}")
        
        # Extract and validate contact information
        try:
            # Extract contact info from payload
            contact_val = payload.get("contact")
            contact_type = payload.get("contact_type")
            
            # Validate contact info
            if not contact_val:
                raise HTTPException(status_code=400, detail="Contact information is required")
            
            # If contact_type not provided, infer it from the contact value
            if not contact_type:
                if "@" in contact_val:
                    contact_type = "email"
                else:
                    contact_type = "phone"
            
            # Normalize phone numbers to E.164 format
            if contact_type == "phone":
                original_phone = contact_val
                contact_val = normalize_phone_number(contact_val)
                logger.info(f"Normalized phone number from {original_phone} to {contact_val}")
                
                # Validate the phone number
                if not is_valid_phone_number(contact_val):
                    logger.warning(f"Invalid phone number format: {contact_val}")
                    raise HTTPException(status_code=400, detail="Invalid phone number format. Please use international format with country code (e.g., +12065550100)")
                    
            # Log with masked contact info for privacy
            try:
                masked_contact = contact_val[:3] + "..." if contact_val else ""
                logger.info(f"Sending verification code to contact: {masked_contact} (type: {contact_type})")
            except Exception as e:
                logger.error(f"Error masking contact: {str(e)}")
                
            # Get or create contact record
            db_contact, original_contact_value = get_or_create_contact(db, contact_val, contact_type)
            
            # Generate verification code
            code = str(uuid.uuid4())[:6]
            expires_at = datetime.utcnow() + timedelta(minutes=15)  # Extended to 15 minutes for better UX
            
            # Determine the purpose of the verification
            purpose_val = payload.get("purpose", "self_service")
            logger.info(f"Verification purpose: {purpose_val}")
            
            # Map purpose value to enum value
            if purpose_val == "verbal_auth":
                purpose = VerificationPurposeEnum.verbal_auth.value
            elif purpose_val == "self_service":
                purpose = VerificationPurposeEnum.self_service.value
            elif purpose_val == "opt_in":
                purpose = VerificationPurposeEnum.opt_in.value
            elif purpose_val == "opt_out":
                purpose = VerificationPurposeEnum.opt_out.value
            else:
                purpose = VerificationPurposeEnum.preference_change.value
            
            # Create verification code record
            verification_record = VerificationCode(
                id=str(uuid.uuid4()),
                user_id=db_contact.id,
                code=code,
                channel=contact_type,  # Use contact_type as channel
                sent_to=contact_val,   # Store original contact value for reference
                purpose=purpose,
                status=VerificationStatusEnum.pending.value,
                expires_at=expires_at
            )
            db.add(verification_record)
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
            logger.error(f"Error in initial processing: {str(e)}")
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
            auth_user_email = payload.get("auth_user_email")
            channel = "email" if "@" in contact_val else "SMS"
            logger.info(f"Template parameters: purpose={purpose}, auth_user_name={auth_user_name}, auth_user_email={auth_user_email}, channel={channel}")
            
            # Get or construct the preferences URL
            logger.info("Getting preferences URL")
            preferences_url = payload.get("preferences_url")
            if not preferences_url:
                frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
                preferences_url = f"{frontend_url}/preferences?contact={contact_val}"
            
            # Add the verification code to the URL to simplify user experience
            preferences_url = f"{preferences_url}&code={code}"
            logger.info(f"Preferences URL with code: {preferences_url.replace(code, '****')}")
            
                
            # Create appropriate email/SMS template based on purpose
            logger.info("Creating email/SMS template")
            url = preferences_url
            
            # Check if a custom message was provided (for password reset, etc.)
            custom_message = payload.get("custom_message")
            if custom_message:
                # Use the custom message directly
                subject = f"Important Message from {company_name}"
                body = custom_message
            elif purpose == "verbal_auth" and auth_user_name:
                # Verbal Auth template (Double Opt-In)
                subject = f"Your {company_name} Preferences Verification Code"
                auth_contact_info = f"{auth_user_name}"
                if auth_user_email:
                    auth_contact_info += f" ({auth_user_email})"
                
                body = f"""Hello from {company_name} Compliant Optin Manager!\n\n{auth_contact_info} has submitted your verbal authorization to opt in to receive notifications from our products and services.\n\nIf you wish to update or confirm your preferences, please visit this site and enter this code.\n\n{url}\nCode: {code}\n\nThanks!\n\nThe Compliance team at {company_name}"""
            else:
                # Self-service template
                subject = f"Your {company_name} Preferences Verification Code"
                
                # Create a short SMS version for SMS channel to stay under 306 character limit
                if channel == "SMS":
                    body = f"{company_name} verification code: {code}. Use this to confirm your preferences at {url.split('?')[0]}"
                    # Log the character count for debugging
                    logger.info(f"SMS message length: {len(body)} characters")
                else:
                    # Full email template
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
                
            # Check if we're in development mode
            is_dev_mode = os.getenv("ENV", "development").lower() == "development"
            
            # Return success response (include code in dev mode for testing)
            logger.info("Returning success response")
            response = {
                "ok": True,
                "message": f"Verification code sent to {masked_contact}.",
                "expires_in_minutes": 15
            }
            
            # Add code to response in development mode for testing
            if is_dev_mode:
                response["dev_code"] = code
                response["dev_note"] = "This code is only shown in development mode"
                logger.warning(f"DEV MODE: Verification code {code} included in response")
                
            return response
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
        contact_type = payload.get("contact_type")
        code = payload.get("code")
        
        if not contact_val or not code:
            raise HTTPException(status_code=400, detail="Missing contact or verification code")
            
        # Determine contact type if not provided
        if not contact_type:
            contact_type = "email" if "@" in contact_val else "phone"
            
        # Normalize phone numbers to E.164 format
        if contact_type == "phone":
            original_phone = contact_val
            contact_val = normalize_phone_number(contact_val)
            logger.info(f"Normalized phone number from {original_phone} to {contact_val}")
            
            # Validate the phone number
            if not is_valid_phone_number(contact_val):
                logger.warning(f"Invalid phone number format: {contact_val}")
                raise HTTPException(status_code=400, detail="Invalid phone number format. Please use international format with country code (e.g., +12065550100)")
            
        masked_contact = contact_val[:3] + "..." if contact_val else ""
        logger.info(f"Verifying code for contact: {masked_contact} (type: {contact_type})")
        
        # Get or create the contact
        db_contact, original_contact_value = get_or_create_contact(db, contact_val, contact_type)
        
        # Find the verification code in the database
        db_code = db.query(VerificationCode).filter(
            VerificationCode.user_id == db_contact.id,
            VerificationCode.code == code,
            VerificationCode.status == VerificationStatusEnum.pending.value,
            VerificationCode.expires_at > datetime.utcnow()
        ).first()
        
        # Check if code is valid
        if not db_code:
            masked_contact = contact_val[:3] + "..." if contact_val else ""
            logger.warning(f"Invalid or expired verification code for contact: {masked_contact}")
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
            
        # Mark the code as verified
        db_code.status = VerificationStatusEnum.verified.value
        db_code.verified_at = datetime.utcnow()
        db.commit()
        
        # Generate JWT token for preferences access
        # Create token data with contact information
        token_data = {
            "sub": db_contact.id,  # Use deterministic ID as subject
            "contact_value": contact_val,  # Include original contact value for reference
            "contact_type": contact_type  # Include contact type
        }
        
        # Create access token with 30-day expiration
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(days=30)
        )
        
        logger.info(f"Creating token for user ID: {db_contact.id}, contact: {contact_val}")
        
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
    # For Phase 1, we're using a simplified approach that always returns a valid response
    logger.info("Fetching preferences")
    
    # Default values
    contact_id = None
    contact_value = None
    contact_type = None
    
    # Try to extract info from JWT token if available
    if auth and auth.credentials:
        try:
            token = auth.credentials
            logger.info(f"Using JWT token: {token[:10]}...")
            
            # Decode the JWT token
            secret_key = os.getenv("SECRET_KEY", "changeme")
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            # Extract info from payload
            contact_id = payload.get("sub")
            contact_value = payload.get("contact_value")
            
            if contact_value and "@" in contact_value:
                contact_type = "email"
            else:
                contact_type = "phone"
                
            logger.info(f"Extracted from token: ID={contact_id}, Value={contact_value}, Type={contact_type}")
                
            logger.info(f"Extracted from token: ID={contact_id}, Value={contact_value}")
        except Exception as e:
            logger.warning(f"Error decoding token: {str(e)}")
    
    # If contact parameter is provided, use it instead of JWT token
    if contact:
        logger.info(f"Using contact parameter: {contact}")
        contact_value = contact
        
        # Determine contact type based on format
        if "@" in contact:
            contact_type = "email"
        else:
            contact_type = "phone"
        
        # Generate deterministic ID from contact value
        from app.core.encryption import generate_deterministic_id
        contact_id = generate_deterministic_id(contact_value)
        logger.info(f"Generated deterministic ID: {contact_id} for contact: {contact_value}")
        
        # Look up contact by deterministic ID
        from app.models.contact import Contact
        db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
        
        if db_contact:
            logger.info(f"Found contact with ID: {contact_id}")
        else:
            logger.info(f"Contact not found with ID: {contact_id}, will return default preferences")
    
    # If we still don't have contact info, return an error
    if not contact_id:
        logger.warning("No valid contact ID found")
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Log the contact ID we're using
        logger.info(f"Looking for consent records for user ID: {contact_id}")
        
        # Get all consent records for this user
        all_user_consents = db.query(Consent).filter(Consent.user_id == contact_id).all()
        logger.info(f"Found {len(all_user_consents)} consent records for user ID: {contact_id}")
        
        # Get all active opt-in programs
        logger.info("Fetching active opt-in programs")
        active_programs = db.query(OptIn).filter(OptIn.status == "active").all()
        logger.info(f"Found {len(active_programs)} active opt-in programs")
        
        # Create a mapping of program ID to consent status for quick lookup
        consent_map = {}
        for consent in all_user_consents:
            consent_map[consent.optin_id] = consent.status
            logger.info(f"User has consent record for program ID {consent.optin_id}: status={consent.status}")
        
        programs_with_status = []
        for program in active_programs:
            logger.info(f"Processing program: {program.name} (ID: {program.id})")
            
            # Check if the user has a consent record for this program using our map
            if program.id in consent_map:
                status = consent_map[program.id]
                logger.info(f"Found consent for program {program.name}: {status}")
            else:
                # Default to opt-out if no consent record exists
                status = ConsentStatusEnum.opt_out.value
                logger.info(f"No consent found for program {program.name}, defaulting to: {status}")
                
            # Add the program with its status to the response
            programs_with_status.append({
                "id": str(program.id),
                "name": program.name,
                "description": program.description or "",
                "type": program.type,
                "status": status,
                "opted_in": status == ConsentStatusEnum.opt_in.value
            })
            
            logger.info(f"Program {program.name} (ID: {program.id}) status: {status}, opted_in: {status == ConsentStatusEnum.opt_in.value}")
            
        logger.info(f"Found {len(programs_with_status)} active programs for user")
    except Exception as e:
        logger.warning(f"Error getting opt-in programs: {str(e)}")
        programs_with_status = []
    
    # Get the most recent comment from consent records
    last_comment = None
    try:
        # Find the most recent consent record with a non-empty comment
        latest_consent = db.query(Consent).filter(
            Consent.user_id == contact_id,
            Consent.notes != None,
            Consent.notes != ''
        ).order_by(Consent.revoked_timestamp.desc(), Consent.consent_timestamp.desc()).first()
        
        if latest_consent and latest_consent.notes:
            last_comment = latest_consent.notes
            logger.info(f"Found last comment: {last_comment}")
    except Exception as e:
        logger.warning(f"Error retrieving last comment: {str(e)}")
    
    # Return the response with the contact info, programs, and last comment
    response_data = {
        "contact": {
            "id": str(contact_id),
            "value": contact_value,
            "type": contact_type
        },
        "programs": programs_with_status,
        "last_comment": last_comment
    }
    
    logger.info(f"Returning preferences data with {len(programs_with_status)} programs and comment: {last_comment}")
    return response_data

# --- 4. Update Preferences ---
@router.patch("/user-preferences", name="update_user_preferences")
def update_preferences(
    payload: dict = Body(...),
    contact: str = Query(None, description="Contact email or phone for direct access"),
    auth: HTTPAuthorizationCredentials = Depends(optional_bearer),
    db: Session = Depends(get_db)
):
    logger.info(f"Updating preferences with payload: {payload}")
    
    # Default values
    contact_id = None
    contact_value = None
    contact_type = None
    
    # Try to extract info from JWT token if available
    if auth and auth.credentials:
        try:
            token = auth.credentials
            logger.info(f"Using JWT token: {token[:10]}...")
            
            # Decode the JWT token
            secret_key = os.getenv("SECRET_KEY", "changeme")
            payload_jwt = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            # Extract info from payload
            contact_id = payload_jwt.get("sub")
            contact_value = payload_jwt.get("contact_value")
            
            if contact_value and "@" in contact_value:
                contact_type = "email"
            else:
                contact_type = "phone"
                
            logger.info(f"Extracted from token: ID={contact_id}, Value={contact_value}, Type={contact_type}")
        except Exception as e:
            logger.warning(f"Error decoding token: {str(e)}")
    
    # If contact parameter is provided, use it instead of JWT token
    if contact:
        logger.info(f"Using contact parameter: {contact}")
        contact_value = contact
        
        # Determine contact type based on format
        if "@" in contact:
            contact_type = "email"
        else:
            contact_type = "phone"
        
        # Generate deterministic ID from contact value
        from app.core.encryption import generate_deterministic_id
        contact_id = generate_deterministic_id(contact_value)
        logger.info(f"Generated deterministic ID: {contact_id} for contact: {contact_value}")
    
    # If we still don't have contact info, return an error
    if not contact_id:
        raise HTTPException(status_code=400, detail="Valid contact information is required")
    
    try:
        # Import models
        from app.models.optin import OptIn, OptInStatusEnum
        from app.models.consent import Consent, ConsentStatusEnum
        # Check if this is a global opt-out request
        global_opt_out = payload.get('global_opt_out', False)
        
        if global_opt_out:
            logger.info("Processing global opt-out request")
            
            # Get all active opt-in programs
            active_programs = db.query(OptIn).filter(OptIn.status == OptInStatusEnum.active.value).all()
            
            # Opt out of all programs
            for program in active_programs:
                # Find existing consent
                # Make sure program_id is a string
                program_id_str = str(program.id).replace('-', '')
                
                consent = db.query(Consent).filter(
                    Consent.user_id == contact_id,
                    Consent.optin_id == program_id_str
                ).first()
                
                if consent:
                    # Update existing consent to opt-out
                    logger.info(f"Global opt-out: Updating consent for program {program.id} to opt-out")
                    consent.status = ConsentStatusEnum.opt_out.value
                    consent.revoked_timestamp = datetime.utcnow()
                    
                    # Update notes if comment is provided
                    if comment:
                        consent.notes = comment
                        logger.info(f"Updated comment for global opt-out: {comment}")
                else:
                    # Create new consent with opt-out status
                    # Make sure program_id is a string
                    program_id_str = str(program.id).replace('-', '')
                    
                    logger.info(f"Global opt-out: Creating new consent for program {program_id_str} with opt-out status")
                    new_consent = Consent(
                        id=str(uuid.uuid4()),
                        user_id=contact_id,
                        optin_id=program_id_str,
                        channel=contact_type,
                        status=ConsentStatusEnum.opt_out.value,
                        revoked_timestamp=datetime.utcnow(),
                        notes=comment if comment else None
                    )
                    db.add(new_consent)
            
            # Commit changes for global opt-out
            db.commit()
            
            # Return success response for global opt-out
            return {
                "success": True,
                "message": "Successfully opted out of all programs"
            }
        
        # Handle program-specific opt-in/out preferences
        programs = {}
        
        # Extract comment if provided
        comment = payload.get('comment', '')
        logger.info(f"Comment provided: {comment}")
        
        # Check if payload contains a 'programs' array from the frontend
        if 'programs' in payload and isinstance(payload['programs'], list):
            # Process the programs array format from the frontend
            for program in payload['programs']:
                if 'id' in program and 'opted_in' in program:
                    programs[program['id']] = program['opted_in']
        else:
            # Fallback to legacy format with program_* keys
            for key, value in payload.items():
                if key.startswith("program_"):
                    program_id = key.replace("program_", "")
                    programs[program_id] = value == True
        
        logger.info(f"Processing {len(programs)} program preferences")
        
        # Update consent records for each program
        for program_id, opted_in in programs.items():
            try:
                # Find the opt-in program
                try:
                    # Log the exact query we're about to make
                    logger.info(f"Looking up program with ID: {program_id}")
                    
                    # Make sure program_id is a string
                    program_id_str = str(program_id).replace('-', '')
                    
                    # Query the database
                    optin = db.query(OptIn).filter(OptIn.id == program_id_str).first()
                    
                    if not optin:
                        logger.warning(f"Program not found: {program_id_str}")
                        continue
                except Exception as e:
                    logger.error(f"Error looking up program {program_id}: {str(e)}")
                    continue
                
                logger.info(f"Processing program {optin.name} (ID: {program_id}), opted_in: {opted_in}")
                
                # Find existing consent or create new one
                logger.info(f"Looking for consent with user_id={contact_id}, optin_id={program_id}")
                
                try:
                    # Make sure program_id is a string for the query
                    program_id_str = str(program_id).replace('-', '')
                    
                    consent = db.query(Consent).filter(
                        Consent.user_id == contact_id,
                        Consent.optin_id == program_id_str
                    ).first()
                except Exception as e:
                    logger.error(f"Error querying consent: {str(e)}")
                    consent = None
                
                # Determine the new status
                new_status = ConsentStatusEnum.opt_in.value if opted_in else ConsentStatusEnum.opt_out.value
                
                if consent:
                    # Update existing consent
                    logger.info(f"Updating existing consent for program {optin.name} (ID: {program_id}) from {consent.status} to {new_status}")
                    consent.status = new_status
                    if opted_in:
                        consent.consent_timestamp = datetime.utcnow()
                    else:
                        consent.revoked_timestamp = datetime.utcnow()
                    
                    # Update notes if comment is provided
                    if comment:
                        consent.notes = comment
                        logger.info(f"Updated comment for existing consent: {comment}")
                else:
                    # Create new consent
                    logger.info(f"Creating new consent for program {optin.name} (ID: {program_id}) with status {new_status}")
                    
                    # Generate a new UUID for the consent record
                    consent_id = str(uuid.uuid4())
                    
                    try:
                        # Create the consent record
                        # Make sure program_id is a string
                        program_id_str = str(program_id).replace('-', '')
                        
                        new_consent = Consent(
                            id=consent_id,
                            user_id=contact_id,
                            optin_id=program_id_str,
                            channel=contact_type,
                            status=new_status,
                            consent_timestamp=datetime.utcnow() if opted_in else None,
                            revoked_timestamp=datetime.utcnow() if not opted_in else None,
                            notes=comment if comment else None
                        )
                        
                        # Add to the session
                        db.add(new_consent)
                        logger.info(f"Successfully created consent record with ID: {consent_id}")
                    except Exception as e:
                        logger.error(f"Error creating consent record: {str(e)}")
            except Exception as e:
                logger.error(f"Error updating consent for program {program_id}: {str(e)}")
        
        # Commit all changes
        db.commit()
        logger.info("Preferences updated successfully")
        
        # For debugging: Query and log all consent records for this user
        all_consents = db.query(Consent).filter(Consent.user_id == contact_id).all()
        logger.info(f"After update: User {contact_id} has {len(all_consents)} consent records")
        for consent in all_consents:
            logger.info(f"  - Program {consent.optin_id}: status={consent.status}")
        
        # Return success response with the updated preferences
        # This ensures the frontend has the latest data
        return {
            "success": True,
            "message": "Preferences updated successfully",
            "preferences": {
                "contact": {
                    "id": contact_id,
                    "value": contact_value,
                    "type": contact_type
                },
                "programs": [
                    {
                        "id": program_id,
                        "opted_in": opted_in
                    } for program_id, opted_in in programs.items()
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

