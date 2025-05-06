import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Customization(Base):
    __tablename__ = "customization"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    logo_path = Column(String, nullable=True)
    primary_color = Column(String, nullable=True)
    secondary_color = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    privacy_policy_url = Column(String, nullable=True)
    email_provider = Column(String, nullable=True)  # e.g., 'aws_ses', 'sendgrid', etc.
    sms_provider = Column(String, nullable=True)    # e.g., 'aws_sns', 'twilio', etc.
    email_connection_status = Column(String, nullable=True)  # 'untested', 'tested', 'failed'
    sms_connection_status = Column(String, nullable=True)    # 'untested', 'tested', 'failed'
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
