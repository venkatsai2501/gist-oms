from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority, TaskType


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    department: str
    departments_involved: Optional[str] = None
    task_type: TaskType = TaskType.DEPARTMENT
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    assigned_to_id: int
    parent_task_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)


class TaskEscalate(BaseModel):
    escalation_reason: str = Field(..., min_length=10)


class TaskResponse(TaskBase):
    id: int
    assigned_to_id: int
    assigned_by_id: int
    status: TaskStatus
    is_escalated: bool
    escalation_reason: Optional[str] = None
    escalated_at: Optional[datetime] = None
    parent_task_id: Optional[int] = None
    progress_percentage: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskCommentCreate(BaseModel):
    comment: str = Field(..., min_length=1)


class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
