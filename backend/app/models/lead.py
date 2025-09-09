from sqlalchemy import Column, String, ForeignKey, Enum, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import LeadStatus, AttributionSource

class Lead(BaseModel):
    __tablename__ = "leads"
    
    # Basic Info
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), index=True)
    phone = Column(String(20), index=True)
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Status
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    
    # Attribution
    source = Column(Enum(AttributionSource), default=AttributionSource.ORGANIC)
    campaign_id = Column(String(255))
    ad_id = Column(String(255))
    keyword = Column(String(255))
    landing_page = Column(String(500))
    referrer = Column(String(500))
    
    # Scoring
    lead_score = Column(Float, default=0.0)
    
    # Custom Fields
    custom_fields = Column(JSON, default=dict)
    notes = Column(String)
    
    # External IDs
    chatwoot_contact_id = Column(String(255), unique=True)
    external_id = Column(String(255))
    
    # Tenant
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="leads")
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="lead", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="lead", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="lead", cascade="all, delete-orphan")
    attributions = relationship("Attribution", back_populates="lead", cascade="all, delete-orphan")