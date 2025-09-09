from sqlalchemy import Column, String, ForeignKey, Enum, DateTime, Float, Text, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import BookingStatus

class Booking(BaseModel):
    __tablename__ = "bookings"
    
    # Booking Info
    booking_number = Column(String(50), unique=True, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    
    # Schedule
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer, default=120)
    
    # Service Details
    services = Column(JSON, nullable=False)
    special_instructions = Column(Text)
    
    # Pricing (from quote if available)
    total_amount = Column(Float)
    deposit_amount = Column(Float)
    deposit_paid = Column(Boolean, default=False)
    
    # Confirmation
    confirmed_at = Column(DateTime(timezone=True))
    confirmation_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    
    # Completion
    completed_at = Column(DateTime(timezone=True))
    completion_notes = Column(Text)
    completion_photos = Column(JSON, default=list)
    
    # External IDs
    calcom_booking_id = Column(String(255), unique=True)
    google_calendar_event_id = Column(String(255))
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="bookings")
    lead = relationship("Lead", back_populates="bookings")
    quote = relationship("Quote", back_populates="booking")
    review = relationship("Review", back_populates="booking", uselist=False)