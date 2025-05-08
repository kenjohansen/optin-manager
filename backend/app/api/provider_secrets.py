"""
api/provider_secrets.py

API endpoints for managing communication provider credentials.

This module provides endpoints for securely storing, retrieving, and testing
credentials for communication providers (email and SMS services). It uses the
ProviderSecretsVault to encrypt sensitive API keys and tokens at rest.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.deps import require_admin_user
from app.core.provider_vault import ProviderSecretsVault
from starlette.status import HTTP_204_NO_CONTENT
import warnings

router = APIRouter(prefix="/provider-secrets", tags=["provider-secrets"])

# Initialize the provider secrets vault
vault = ProviderSecretsVault()

def set_secret(key: str, value: str):
    """
    Store a provider credential in the vault.
    
    Args:
        key (str): The identifier for the secret
        value (str): The secret value to store
    """
    vault.set_secret(key, value)


def get_secret(key: str):
    """
    Retrieve a provider credential from the vault.
    
    Args:
        key (str): The identifier for the secret
        
    Returns:
        str or None: The secret value if found, None otherwise
    """
    return vault.get_secret(key)


def is_secret_configured(key: str):
    """
    Check if a provider credential exists in the vault.
    
    Args:
        key (str): The identifier for the secret
        
    Returns:
        bool: True if the secret exists, False otherwise
    """
    return bool(vault.get_secret(key))


@router.post("/set", dependencies=[Depends(require_admin_user)])
def set_provider_secret(
    provider_type: str = Body(..., embed=True),  # 'email' or 'sms'
    access_key: str = Body(...),
    secret_key: str = Body(...),
    region: str = Body(None),
    from_address: str = Body(None),
):
    """
    Store credentials for a communication provider.
    
    This endpoint allows administrators to securely store API keys and other
    credentials needed for sending messages through email or SMS providers.
    The credentials are encrypted using the ProviderSecretsVault before storage.
    
    As noted in the memories, this supports the customization settings for
    communication providers that are essential for the system's messaging
    capabilities.
    
    Args:
        provider_type (str): Type of provider ('email' or 'sms')
        access_key (str): Provider API key or access key
        secret_key (str): Provider API secret or token
        region (str, optional): Provider region (e.g., AWS region)
        from_address (str, optional): Default sender address
        
    Returns:
        dict: Confirmation of successful storage
        
    Raises:
        HTTPException: 400 if provider_type is invalid
        
    Security:
        Requires admin role authentication
    """
    if provider_type not in ("email", "sms"):
        raise HTTPException(status_code=400, detail="Invalid provider_type")
    set_secret(f"{provider_type.upper()}_ACCESS_KEY", access_key)
    set_secret(f"{provider_type.upper()}_SECRET_KEY", secret_key)
    if region:
        set_secret(f"{provider_type.upper()}_REGION", region)
    if provider_type == "email" and from_address:
        set_secret("EMAIL_FROM_ADDRESS", from_address)
    return {"ok": True}


from app.core.deps import require_support_user

@router.get("/status", dependencies=[Depends(require_support_user)])
def get_secrets_status():
    return {
        "email_configured": is_secret_configured("EMAIL_ACCESS_KEY") and is_secret_configured("EMAIL_SECRET_KEY"),
        "sms_configured": is_secret_configured("SMS_ACCESS_KEY") and is_secret_configured("SMS_SECRET_KEY"),
    }


import os
import boto3
from botocore.exceptions import ClientError

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.customization import Customization

@router.post("/test", dependencies=[Depends(require_admin_user)])
def test_provider_connection(provider_type: str = Body(..., embed=True), db: Session = Depends(get_db)):
    # Check if secrets are set
    if provider_type == "email":
        access_key = get_secret("EMAIL_ACCESS_KEY")
        secret_key = get_secret("EMAIL_SECRET_KEY")
        region = get_secret("EMAIL_REGION") or "us-east-1"
        configured = access_key and secret_key
    elif provider_type == "sms":
        access_key = get_secret("SMS_ACCESS_KEY")
        secret_key = get_secret("SMS_SECRET_KEY")
        region = get_secret("SMS_REGION") or "us-east-1"
        configured = access_key and secret_key
    else:
        raise HTTPException(status_code=400, detail="Invalid provider_type")
    if not configured:
        raise HTTPException(status_code=400, detail="Credentials not configured")

    # If ENV=dev or ENV=mock, return a mocked response and update status
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization()
        db.add(customization)
    if os.getenv("ENV") in ("dev", "mock"):
        if provider_type == "email":
            customization.email_connection_status = "tested"
        elif provider_type == "sms":
            customization.sms_connection_status = "tested"
        db.commit()
        return {"ok": True, "message": f"{provider_type.capitalize()} provider connection test passed (mocked)."}

    # Real connection test
    try:
        if provider_type == "email":
            print(f"[TEST-CONNECT] Email provider: access_key set={bool(access_key)}, secret_key set={bool(secret_key)}, region={region}")
            warnings.warn(f"[TEST-CONNECT] Email provider: access_key set={bool(access_key)}, secret_key set={bool(secret_key)}, region={region}")
            
            # Check for from_address in vault first
            from_address = get_secret("EMAIL_FROM_ADDRESS")
            print(f"[TEST-CONNECT] Email provider: from_address from vault={from_address}")
            
            # Fall back to environment variable if not in vault
            if not from_address:
                from_address = os.getenv("SES_FROM_EMAIL")
                print(f"[TEST-CONNECT] Email provider: from_address from env={from_address}")
            
            # Last resort fallback
            if not from_address:
                from_address = "no-reply@example.com"
                print(f"[TEST-CONNECT] Email provider: using default from_address={from_address}")
            
            print(f"[TEST-CONNECT] Email provider: final from_address={from_address}")
            warnings.warn(f"[TEST-CONNECT] Email provider: final from_address={from_address}")
            
            if from_address == "no-reply@example.com":
                print("[TEST-CONNECT] WARNING: Using default sender email address. This is likely not verified in AWS SES.")
                warnings.warn("[TEST-CONNECT] WARNING: Using default sender email address. This is likely not verified in AWS SES.")
                raise HTTPException(status_code=400, detail="Using default sender email address (no-reply@example.com). Please set a verified sender email address in AWS SES.")
            
            if not from_address:
                print("[TEST-CONNECT] ERROR: Sender email address not set.")
                warnings.warn("[TEST-CONNECT] ERROR: Sender email address not set.")
                raise HTTPException(status_code=400, detail="Sender email address not set. Please specify a sender email address.")
            client = boto3.client(
                "ses",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
            try:
                client.send_email(
                    Source=from_address,
                    Destination={"ToAddresses": [from_address]},
                    Message={
                        "Subject": {"Data": "OptIn Manager Test Connection"},
                        "Body": {"Text": {"Data": f"This is a test email from {from_address}. If you received this, your SES sender is authorized."}},
                    },
                )
                print(f"[TEST-CONNECT] SUCCESS: Test email sent from {from_address} to itself.")
                warnings.warn(f"[TEST-CONNECT] SUCCESS: Test email sent from {from_address} to itself.")
                customization.email_connection_status = "tested"
                db.commit()
                return {"ok": True, "message": f"Email provider connection test passed (real). Test email sent from {from_address} to itself."}
            except ClientError as e:
                print(f"[TEST-CONNECT] FAILURE: Email provider connection failed: {str(e)}")
                warnings.warn(f"[TEST-CONNECT] FAILURE: Email provider connection failed: {str(e)}")
                customization.email_connection_status = "failed"
                db.commit()
                raise HTTPException(status_code=400, detail=f"Email provider connection failed: {str(e)}")
        elif provider_type == "sms":
            test_number = get_secret("SMS_TEST_RECIPIENT") or os.getenv("SMS_TEST_RECIPIENT")
            from_number = get_secret("SMS_FROM_NUMBER") or os.getenv("SMS_FROM_NUMBER")
            print(f"[TEST-CONNECT] SMS provider: access_key set={bool(access_key)}, secret_key set={bool(secret_key)}, region={region}, test_number={test_number}, from_number={from_number}")
            warnings.warn(f"[TEST-CONNECT] SMS provider: access_key set={bool(access_key)}, secret_key set={bool(secret_key)}, region={region}, test_number={test_number}, from_number={from_number}")
            if not test_number:
                raise HTTPException(status_code=400, detail="SMS_TEST_RECIPIENT not set. Please specify a test recipient phone number.")
            client = boto3.client(
                "sns",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
            try:
                client.publish(
                    PhoneNumber=test_number,
                    Message=f"This is a test SMS from OptIn Manager. If you received this, your SMS sender is authorized."
                )
                customization.sms_connection_status = "tested"
                db.commit()
                return {"ok": True, "message": f"SMS provider connection test passed (real). Test SMS sent to {test_number}."}
            except ClientError as e:
                customization.sms_connection_status = "failed"
                db.commit()
                raise HTTPException(status_code=400, detail=f"SMS provider connection failed: {str(e)}")
    except ClientError as e:
        if provider_type == "email":
            customization.email_connection_status = "failed"
        elif provider_type == "sms":
            customization.sms_connection_status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail=f"{provider_type.capitalize()} provider connection failed: {str(e)}")

# Delete provider credentials endpoint
@router.post("/delete", dependencies=[Depends(require_admin_user)])
def delete_provider_secret(provider_type: str = Body(..., embed=True), db: Session = Depends(get_db)):
    if provider_type not in ("email", "sms"):
        raise HTTPException(status_code=400, detail="Invalid provider_type")
    vault.delete_secret(f"{provider_type.upper()}_ACCESS_KEY")
    vault.delete_secret(f"{provider_type.upper()}_SECRET_KEY")
    vault.delete_secret(f"{provider_type.upper()}_REGION")
    customization = db.query(Customization).first()
    if not customization:
        customization = Customization()
        db.add(customization)
    if provider_type == "email":
        customization.email_connection_status = "untested"
    elif provider_type == "sms":
        customization.sms_connection_status = "untested"
    db.commit()
    return {"ok": True, "message": f"{provider_type.capitalize()} provider credentials deleted."}

