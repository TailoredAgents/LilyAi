from sqlalchemy import Column, String, ForeignKey, Enum, Integer, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import ReviewStatus

class Review(BaseModel):
    __tablename__ = "reviews"
    
    # Review Info
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text)
    
    # Request Details
    request_sent_at = Column(DateTime(timezone=True))
    request_method = Column(String(50))  # sms, email
    review_link = Column(String(500))
    
    # Response
    responded_at = Column(DateTime(timezone=True))
    response_platform = Column(String(50))  # google, facebook, yelp, internal
    response_url = Column(String(500))
    
    # Follow-up
    follow_up_sent = Column(Boolean, default=False)
    follow_up_sent_at = Column(DateTime(timezone=True))
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="reviews")
    lead = relationship("Lead", back_populates="reviews")
    booking = relationship("Booking", back_populates="review")