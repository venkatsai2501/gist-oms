from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base import Base


class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TASK_ESCALATED = "task_escalated"
    DOCUMENT_PENDING = "document_pending"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_REJECTED = "document_rejected"
    MEETING_INVITED = "meeting_invited"
    MEETING_APPROVED = "meeting_approved"
    MEETING_CANCELLED = "meeting_cancelled"
    DELEGATION_ASSIGNED = "delegation_assigned"
    SYSTEM = "system"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    is_read = Column(Boolean, default=False, index=True)
    
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    
    action_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime, nullable=True)
    
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title} - {'Read' if self.is_read else 'Unread'}>"
