from sqlalchemy import Column, Integer, String, Text, Boolean, Enum as SQLEnum
from datetime import datetime
from enum import Enum
from app.db.base import Base


class ResourceType(str, Enum):
    MEETING_ROOM = "meeting_room"
    CONFERENCE_HALL = "conference_hall"
    PROJECTOR = "projector"
    VEHICLE = "vehicle"
    EQUIPMENT = "equipment"


class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    description = Column(Text, nullable=True)
    
    capacity = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    
    is_available = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Resource {self.id}: {self.name} - {self.resource_type}>"
