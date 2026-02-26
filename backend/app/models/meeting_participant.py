from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.base import Base


class ParticipantStatus(str, Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"


class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(SQLEnum(ParticipantStatus), default=ParticipantStatus.INVITED, nullable=False)
    is_required = Column(Boolean, default=True)
    
    meeting = relationship("Meeting", backref="participants")
    user = relationship("User", backref="meeting_participations")
    
    def __repr__(self):
        return f"<MeetingParticipant Meeting {self.meeting_id} - User {self.user_id}>"
