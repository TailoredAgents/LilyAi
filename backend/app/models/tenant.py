from sqlalchemy import Column, String, Boolean, Integer, JSON, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import SubscriptionPlan, SubscriptionStatus
import uuid

class Tenant(BaseModel):
    __tablename__ = "tenants"
    
    # Basic Info
    name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    website = Column(String(255))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(2), default="US")
    timezone = Column(String(50), default="America/New_York")
    
    # Subscription
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.TRIAL)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIALING)
    trial_ends_at = Column(DateTime(timezone=True))
    subscription_ends_at = Column(DateTime(timezone=True))
    
    # Stripe
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255), unique=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    quiet_hours_start = Column(Integer, default=21)  # 9 PM
    quiet_hours_end = Column(Integer, default=9)     # 9 AM
    auto_reply_enabled = Column(Boolean, default=True)
    review_delay_hours = Column(Integer, default=24)
    
    # Feature Settings
    settings = Column(JSON, default=dict)
    
    # Limits (based on plan)
    max_users = Column(Integer, default=3)
    max_conversations_per_month = Column(Integer, default=100)
    max_sms_per_month = Column(Integer, default=500)
    
    # Usage Tracking
    current_month_conversations = Column(Integer, default=0)
    current_month_sms = Column(Integer, default=0)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="tenant", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="tenant", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="tenant", cascade="all, delete-orphan")
    pricebooks = relationship("PriceBook", back_populates="tenant", cascade="all, delete-orphan")
    channel_accounts = relationship("ChannelAccount", back_populates="tenant", cascade="all, delete-orphan")
    tenant_settings = relationship("TenantSettings", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="tenant", cascade="all, delete-orphan")
    attributions = relationship("Attribution", back_populates="tenant", cascade="all, delete-orphan")