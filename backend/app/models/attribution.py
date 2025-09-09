from sqlalchemy import Column, String, ForeignKey, Enum, Float, JSON, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import AttributionSource

class Attribution(BaseModel):
    __tablename__ = "attributions"
    
    # Source Info
    source = Column(Enum(AttributionSource), nullable=False)
    medium = Column(String(100))
    campaign = Column(String(255))
    term = Column(String(255))
    content = Column(String(255))
    
    # IDs
    gclid = Column(String(255))  # Google Click ID
    fbclid = Column(String(255))  # Facebook Click ID
    utm_source = Column(String(255))
    utm_medium = Column(String(255))
    utm_campaign = Column(String(255))
    utm_term = Column(String(255))
    utm_content = Column(String(255))
    
    # Performance
    cost = Column(Float, default=0.0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Tracking
    first_touch_at = Column(DateTime(timezone=True))
    last_touch_at = Column(DateTime(timezone=True))
    conversion_at = Column(DateTime(timezone=True))
    
    # Additional Data
    metadata = Column(JSON, default=dict)
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="attributions")
    lead = relationship("Lead", back_populates="attributions")