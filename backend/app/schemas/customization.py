from pydantic import BaseModel
from typing import Optional

class CustomizationOut(BaseModel):
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]

    model_config = {"from_attributes": True}

class CustomizationColorsUpdate(BaseModel):
    primary_color: str
    secondary_color: str
