from pydantic import BaseModel
from typing import Optional

class CustomizationOut(BaseModel):
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]
    company_name: Optional[str]
    privacy_policy_url: Optional[str]
    email_provider: Optional[str]
    sms_provider: Optional[str]
    email_connection_status: Optional[str]
    sms_connection_status: Optional[str]

    model_config = {"from_attributes": True}

class CustomizationColorsUpdate(BaseModel):
    primary_color: str
    secondary_color: str
