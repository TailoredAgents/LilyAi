from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.models.enums import ConversationStatus, ChannelType

class Conversation(BaseModel):
    __tablename__ = "conversations"
    
    # Channel Info
    channel = Column(Enum(ChannelType), nullable=False)
    channel_conversation_id = Column(String(255), unique=True, index=True)
    
    # Status
    status = Column(Enum(ConversationStatus), default=ConversationStatus.OPEN)
    unread_count = Column(Integer, default=0)
    
    # Flags
    is_priority = Column(Boolean, default=False)
    is_escalated = Column(Boolean, default=False)
    requires_human = Column(Boolean, default=False)
    
    # Metadata
    subject = Column(String(500))
    tags = Column(String(500))  # Comma-separated
    
    # External IDs
    chatwoot_conversation_id = Column(String(255), unique=True)
    
    # Foreign Keys
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="conversations")
    lead = relationship("Lead", back_populates="conversations")
    assigned_user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")