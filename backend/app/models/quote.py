from sqlalchemy import Column, String, ForeignKey, Enum, Float, Integer, JSON, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import QuoteStatus, ServiceType

class Quote(BaseModel):
    __tablename__ = "quotes"
    
    # Quote Details
    quote_number = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    
    # Services
    services = Column(JSON, nullable=False)  # List of service items
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Estimates
    estimated_sqft = Column(Float)
    confidence_score = Column(Float)  # AI confidence in quote
    is_ballpark = Column(Boolean, default=True)
    requires_in_person = Column(Boolean, default=False)
    
    # Property Details
    property_photos = Column(JSON, default=list)  # S3 URLs
    property_notes = Column(Text)
    
    # Validity
    valid_until = Column(DateTime(timezone=True))
    
    # Tracking
    sent_at = Column(DateTime(timezone=True))
    viewed_at = Column(DateTime(timezone=True))
    accepted_at = Column(DateTime(timezone=True))
    declined_at = Column(DateTime(timezone=True))
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="quotes")
    lead = relationship("Lead", back_populates="quotes")
    booking = relationship("Booking", back_populates="quote", uselist=False)