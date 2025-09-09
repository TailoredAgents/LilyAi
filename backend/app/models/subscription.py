from sqlalchemy import Column, String, ForeignKey, Enum, Float, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import SubscriptionPlan, SubscriptionStatus

class Subscription(BaseModel):
    __tablename__ = "subscriptions"
    
    # Subscription Info
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False)
    
    # Billing
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    interval = Column(String(20), default="month")  # month, year
    
    # Dates
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    trial_start = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))
    canceled_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    
    # Stripe
    stripe_subscription_id = Column(String(255), unique=True)
    stripe_customer_id = Column(String(255))
    stripe_price_id = Column(String(255))
    stripe_payment_method_id = Column(String(255))
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Flags
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="subscriptions")