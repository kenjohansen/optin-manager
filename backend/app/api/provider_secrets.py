from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.deps import require_admin_user
from app.core.provider_vault import ProviderSecretsVault
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter(prefix="/provider-secrets", tags=["provider-secrets"])

vault = ProviderSecretsVault()
def set_secret(key: str, value: str):
    vault.set_secret(key, value)


def get_secret(key: str):
    return vault.get_secret(key)


def is_secret_configured(key: str):
    return bool(vault.get_secret(key))


@router.post("/set", dependencies=[Depends(require_admin_user)])
def set_provider_secret(
    provider_type: str = Body(..., embed=True),  # 'email' or 'sms'
    access_key: str = Body(...),
    secret_key: str = Body(...),
    region: str = Body(None),
):
    if provider_type not in ("email", "sms"):
        raise HTTPException(status_code=400, detail="Invalid provider_type")
    set_secret(f"{provider_type.upper()}_ACCESS_KEY", access_key)
    set_secret(f"{provider_type.upper()}_SECRET_KEY", secret_key)
    if region:
        set_secret(f"{provider_type.upper()}_REGION", region)
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
            client = boto3.client(
                "ses",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
            client.list_identities(MaxItems=1)
            customization.email_connection_status = "tested"
        elif provider_type == "sms":
            client = boto3.client(
                "sns",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
            client.list_topics()
            customization.sms_connection_status = "tested"
        db.commit()
        return {"ok": True, "message": f"{provider_type.capitalize()} provider connection test passed (real)."}
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

