from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base import Base


class TaskStatus(str, Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(str, Enum):
    DEPARTMENT = "department"
    CROSS_DEPARTMENT = "cross_department"
    INSTITUTE_WIDE = "institute_wide"


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    department = Column(String(100), nullable=False, index=True)
    departments_involved = Column(Text, nullable=True)
    
    task_type = Column(SQLEnum(TaskType), default=TaskType.DEPARTMENT, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.ASSIGNED, nullable=False, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    due_date = Column(DateTime, nullable=True)
    
    is_escalated = Column(Boolean, default=False, index=True)
    escalation_reason = Column(Text, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    progress_percentage = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], backref="assigned_tasks")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id], backref="created_tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    
    def __repr__(self):
        return f"<Task {self.id}: {self.title} - {self.status}>"
