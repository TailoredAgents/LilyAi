from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import ChannelType

class ChannelAccount(BaseModel):
    __tablename__ = "channel_accounts"
    
    # Channel Info
    channel_type = Column(Enum(ChannelType), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Account Details
    account_id = Column(String(255))  # Platform-specific ID
    account_name = Column(String(255))
    
    # Credentials (encrypted in production)
    credentials = Column(JSON, default=dict)
    
    # Configuration
    config = Column(JSON, default=dict)
    webhook_url = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="channel_accounts")