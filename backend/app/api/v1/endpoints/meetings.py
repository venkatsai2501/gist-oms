from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from app.api.deps import get_db, get_current_active_user, require_vp
from app.models.meeting import Meeting, MeetingStatus
from app.models.meeting_participant import MeetingParticipant, ParticipantStatus
from app.models.resource import Resource
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingResponse, MeetingParticipantResponse, ResourceResponse

router = APIRouter()


def check_meeting_conflicts(db: Session, room_id: int, start_time: datetime, end_time: datetime, exclude_meeting_id: int = None) -> bool:
    query = db.query(Meeting).filter(
        Meeting.room_id == room_id,
        Meeting.status.in_([MeetingStatus.APPROVED, MeetingStatus.PENDING]),
        or_(
            and_(Meeting.start_time <= start_time, Meeting.end_time > start_time),
            and_(Meeting.start_time < end_time, Meeting.end_time >= end_time),
            and_(Meeting.start_time >= start_time, Meeting.end_time <= end_time)
        )
    )
    
    if exclude_meeting_id:
        query = query.filter(Meeting.id != exclude_meeting_id)
    
    return query.first() is not None


def check_participant_conflicts(db: Session, user_id: int, start_time: datetime, end_time: datetime, exclude_meeting_id: int = None) -> bool:
    subquery = db.query(MeetingParticipant.meeting_id).filter(
        MeetingParticipant.user_id == user_id,
        MeetingParticipant.status.in_([ParticipantStatus.ACCEPTED, ParticipantStatus.INVITED])
    ).subquery()
    
    query = db.query(Meeting).filter(
        Meeting.id.in_(subquery),
        Meeting.status.in_([MeetingStatus.APPROVED, MeetingStatus.PENDING]),
        or_(
            and_(Meeting.start_time <= start_time, Meeting.end_time > start_time),
            and_(Meeting.start_time < end_time, Meeting.end_time >= end_time),
            and_(Meeting.start_time >= start_time, Meeting.end_time <= end_time)
        )
    )
    
    if exclude_meeting_id:
        query = query.filter(Meeting.id != exclude_meeting_id)
    
    return query.first() is not None


@router.get("/", response_model=List[MeetingResponse])
def get_meetings(
    skip: int = 0,
    limit: int = 100,
    status: MeetingStatus = None,
    my_meetings: bool = False,
    pending_approval: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if my_meetings:
        participant_meeting_ids = db.query(MeetingParticipant.meeting_id).filter(
            MeetingParticipant.user_id == current_user.id
        ).subquery()
        
        query = db.query(Meeting).filter(
            or_(
                Meeting.organizer_id == current_user.id,
                Meeting.id.in_(participant_meeting_ids)
            )
        )
    elif pending_approval and current_user.role.hierarchy_level <= 3:
        query = db.query(Meeting).filter(Meeting.status == MeetingStatus.PENDING)
    else:
        query = db.query(Meeting)
    
    if status:
        query = query.filter(Meeting.status == status)
    
    meetings = query.order_by(Meeting.start_time.desc()).offset(skip).limit(limit).all()
    return meetings


@router.post("/", response_model=MeetingResponse)
def create_meeting(
    meeting_in: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if meeting_in.start_time >= meeting_in.end_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    if meeting_in.room_id:
        room = db.query(Resource).filter(Resource.id == meeting_in.room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        if check_meeting_conflicts(db, meeting_in.room_id, meeting_in.start_time, meeting_in.end_time):
            raise HTTPException(status_code=400, detail="Room is already booked for this time slot")
    
    for participant_id in meeting_in.participant_ids:
        if check_participant_conflicts(db, participant_id, meeting_in.start_time, meeting_in.end_time):
            user = db.query(User).filter(User.id == participant_id).first()
            raise HTTPException(
                status_code=400, 
                detail=f"Participant {user.full_name if user else participant_id} has a conflicting meeting"
            )
    
    meeting_data = meeting_in.model_dump(exclude={"participant_ids"})
    meeting = Meeting(
        **meeting_data,
        organizer_id=current_user.id,
        status=MeetingStatus.PENDING if current_user.role.hierarchy_level > 3 else MeetingStatus.APPROVED
    )
    
    if current_user.role.hierarchy_level <= 3:
        meeting.approved_by_id = current_user.id
        meeting.approved_at = datetime.utcnow()
    
    db.add(meeting)
    db.flush()
    
    for participant_id in meeting_in.participant_ids:
        participant = MeetingParticipant(
            meeting_id=meeting.id,
            user_id=participant_id,
            status=ParticipantStatus.INVITED
        )
        db.add(participant)
        
        notification = Notification(
            user_id=participant_id,
            notification_type=NotificationType.MEETING_INVITED,
            title="Meeting Invitation",
            message=f"You are invited to meeting: {meeting.title}",
            related_entity_type="meeting",
            related_entity_id=meeting.id,
            action_url=f"/meetings/{meeting.id}"
        )
        db.add(notification)
    
    if meeting.status == MeetingStatus.PENDING:
        vp_users = db.query(User).filter(User.role_id == 3).all()
        for vp_user in vp_users:
            notification = Notification(
                user_id=vp_user.id,
                notification_type=NotificationType.MEETING_INVITED,
                title="Meeting Approval Required",
                message=f"Meeting '{meeting.title}' requires approval",
                related_entity_type="meeting",
                related_entity_id=meeting.id,
                action_url=f"/meetings/{meeting.id}"
            )
            db.add(notification)
    
    db.commit()
    db.refresh(meeting)
    
    return meeting


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meeting


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    meeting_id: int,
    meeting_in: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.organizer_id != current_user.id and current_user.role.hierarchy_level > 3:
        raise HTTPException(status_code=403, detail="Not authorized to update this meeting")
    
    update_data = meeting_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(meeting, field, value)
    
    db.commit()
    db.refresh(meeting)
    
    return meeting


@router.post("/{meeting_id}/approve", response_model=MeetingResponse)
def approve_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vp)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.status != MeetingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Meeting is not pending approval")
    
    meeting.status = MeetingStatus.APPROVED
    meeting.approved_by_id = current_user.id
    meeting.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(meeting)
    
    notification = Notification(
        user_id=meeting.organizer_id,
        notification_type=NotificationType.MEETING_APPROVED,
        title="Meeting Approved",
        message=f"Your meeting '{meeting.title}' has been approved",
        related_entity_type="meeting",
        related_entity_id=meeting.id,
        action_url=f"/meetings/{meeting.id}"
    )
    db.add(notification)
    db.commit()
    
    return meeting


@router.post("/{meeting_id}/reject", response_model=MeetingResponse)
def reject_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vp)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.status != MeetingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Meeting is not pending approval")
    
    meeting.status = MeetingStatus.REJECTED
    
    db.commit()
    db.refresh(meeting)
    
    notification = Notification(
        user_id=meeting.organizer_id,
        notification_type=NotificationType.MEETING_CANCELLED,
        title="Meeting Rejected",
        message=f"Your meeting '{meeting.title}' has been rejected",
        related_entity_type="meeting",
        related_entity_id=meeting.id,
        action_url=f"/meetings/{meeting.id}"
    )
    db.add(notification)
    db.commit()
    
    return meeting


@router.get("/{meeting_id}/participants", response_model=List[MeetingParticipantResponse])
def get_meeting_participants(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    participants = db.query(MeetingParticipant).filter(
        MeetingParticipant.meeting_id == meeting_id
    ).all()
    
    return participants


@router.get("/resources/", response_model=List[ResourceResponse])
def get_resources(
    resource_type: str = None,
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Resource)
    
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    
    if available_only:
        query = query.filter(Resource.is_available == True)
    
    resources = query.all()
    return resources
