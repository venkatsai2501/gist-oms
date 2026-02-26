from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base import Base


class MeetingStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MeetingPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    
    room_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    location = Column(String(255), nullable=True)
    
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(MeetingPriority), default=MeetingPriority.MEDIUM, nullable=False)
    
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organizer = relationship("User", foreign_keys=[organizer_id], backref="organized_meetings")
    approved_by = relationship("User", foreign_keys=[approved_by_id], backref="approved_meetings")
    room = relationship("Resource", backref="meetings")
    
    def __repr__(self):
        return f"<Meeting {self.id}: {self.title} - {self.status}>"
