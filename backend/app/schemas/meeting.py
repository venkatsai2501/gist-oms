from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.meeting import MeetingStatus, MeetingPriority
from app.models.meeting_participant import ParticipantStatus


class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    room_id: Optional[int] = None
    location: Optional[str] = None
    priority: MeetingPriority = MeetingPriority.MEDIUM
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


class MeetingCreate(MeetingBase):
    participant_ids: List[int] = []


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[MeetingStatus] = None
    location: Optional[str] = None


class MeetingResponse(MeetingBase):
    id: int
    organizer_id: int
    status: MeetingStatus
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MeetingParticipantResponse(BaseModel):
    id: int
    meeting_id: int
    user_id: int
    status: ParticipantStatus
    is_required: bool
    
    class Config:
        from_attributes = True


class ResourceBase(BaseModel):
    name: str
    resource_type: str
    description: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None


class ResourceResponse(ResourceBase):
    id: int
    is_available: bool
    requires_approval: bool
    
    class Config:
        from_attributes = True
