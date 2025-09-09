from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, Text, JSON, DateTime, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import MessageDirection, MessageStatus

class Message(BaseModel):
    __tablename__ = "messages"
    
    # Content
    content = Column(Text, nullable=False)
    direction = Column(Enum(MessageDirection), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING)
    
    # Metadata
    is_ai_generated = Column(Boolean, default=False)
    confidence_score = Column(Float)
    intent = Column(String(100))  # quote_request, booking_request, complaint, etc.
    sentiment = Column(String(50))  # positive, negative, neutral
    
    # Attachments
    attachments = Column(JSON, default=list)  # List of URLs
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))  # For jittered messages
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # External IDs
    chatwoot_message_id = Column(String(255), unique=True)
    external_message_id = Column(String(255))  # Twilio SID, Meta message ID, etc.
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Foreign Keys
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # If sent by a user
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")