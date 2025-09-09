from sqlalchemy import Column, String, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import ServiceType, MaterialType, Severity

class PriceBook(BaseModel):
    __tablename__ = "pricebooks"
    
    # Service Info
    name = Column(String(255), nullable=False)
    service_type = Column(Enum(ServiceType), nullable=False)
    description = Column(String(500))
    
    # Pricing
    base_price = Column(Float, nullable=False)  # Base price
    price_per_sqft = Column(Float, default=0.0)  # Per square foot
    minimum_charge = Column(Float, default=0.0)
    
    # Multipliers
    material_multipliers = Column(JSON, default=dict)  # {"vinyl": 1.0, "brick": 1.2, ...}
    severity_multipliers = Column(JSON, default=dict)  # {"light": 0.8, "moderate": 1.0, "heavy": 1.3}
    
    # Rules
    is_active = Column(Boolean, default=True)
    requires_in_person = Column(Boolean, default=False)
    
    # Additional Charges
    addon_charges = Column(JSON, default=dict)  # {"gutter_guards": 50, "second_story": 25, ...}
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="pricebooks")