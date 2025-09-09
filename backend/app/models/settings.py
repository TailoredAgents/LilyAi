from sqlalchemy import Column, String, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class TenantSettings(BaseModel):
    __tablename__ = "tenant_settings"
    
    # Cal.com Settings
    calcom_embed_url = Column(String(500))
    calcom_api_key = Column(String(255))
    calcom_event_type_id = Column(String(255))
    
    # Google Calendar
    google_calendar_id = Column(String(255))
    google_refresh_token = Column(String(500))
    
    # Messaging Templates
    welcome_message = Column(String(1000), default="Hi! Thanks for reaching out. How can we help you today?")
    quote_request_message = Column(String(1000), default="I'd be happy to provide a quote! Please share photos of the area and your address.")
    booking_confirmation_message = Column(String(1000), default="Your appointment is confirmed for {date} at {time}. We'll see you then!")
    review_request_message = Column(String(1000), default="Thank you for choosing us! We'd love to hear about your experience: {review_link}")
    
    # AI Settings
    ai_tone = Column(String(50), default="friendly")  # friendly, professional, casual
    ai_escalation_keywords = Column(JSON, default=["manager", "complaint", "urgent", "problem", "speak to human"])
    ai_quote_keywords = Column(JSON, default=["quote", "price", "cost", "estimate", "how much"])
    
    # Business Hours
    business_hours = Column(JSON, default={
        "monday": {"open": "08:00", "close": "18:00"},
        "tuesday": {"open": "08:00", "close": "18:00"},
        "wednesday": {"open": "08:00", "close": "18:00"},
        "thursday": {"open": "08:00", "close": "18:00"},
        "friday": {"open": "08:00", "close": "18:00"},
        "saturday": {"open": "09:00", "close": "14:00"},
        "sunday": {"closed": True}
    })
    
    # Auto-Reply Rules
    auto_reply_delay_seconds = Column(Integer, default=30)
    max_auto_replies_per_conversation = Column(Integer, default=5)
    
    # Review Settings
    review_platforms = Column(JSON, default=["google", "facebook"])
    review_request_delay_hours = Column(Integer, default=24)
    
    # Branding
    logo_url = Column(String(500))
    brand_color = Column(String(7), default="#2563eb")
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), unique=True, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="tenant_settings")