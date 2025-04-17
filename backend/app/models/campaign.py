from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class CampaignTypeEnum(str, Enum):
    transactional = "transactional"
    promotional = "promotional"

class CampaignStatusEnum(str, Enum):
    active = "active"
    paused = "paused"
    archived = "archived"

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, default=CampaignTypeEnum.transactional)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default=CampaignStatusEnum.active)
