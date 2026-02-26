from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from app.api.deps import get_db, get_current_active_user
from app.core.permissions import PermissionChecker
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.task_comment import TaskComment
from app.models.notification import Notification, NotificationType
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskEscalate, TaskCommentCreate, TaskCommentResponse

router = APIRouter()
permission_checker = PermissionChecker()


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus = None,
    department: str = None,
    assigned_to_me: bool = False,
    escalated_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Task)
    
    if assigned_to_me:
        query = query.filter(Task.assigned_to_id == current_user.id)
    elif current_user.role.hierarchy_level == 5:
        query = query.filter(Task.assigned_to_id == current_user.id)
    elif current_user.role.hierarchy_level == 4:
        query = query.filter(Task.department == current_user.department)
    elif current_user.role.hierarchy_level <= 3:
        if department:
            query = query.filter(Task.department == department)
    
    if status:
        query = query.filter(Task.status == status)
    
    if escalated_only:
        query = query.filter(Task.is_escalated == True)
    
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    assignee = db.query(User).filter(User.id == task_in.assigned_to_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found")
    
    if not permission_checker.can_assign_task(current_user, assignee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign tasks to users with higher hierarchy level"
        )
    
    task = Task(
        **task_in.model_dump(),
        assigned_by_id=current_user.id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    notification = Notification(
        user_id=task.assigned_to_id,
        notification_type=NotificationType.TASK_ASSIGNED,
        title="New Task Assigned",
        message=f"You have been assigned a new task: {task.title}",
        related_entity_type="task",
        related_entity_id=task.id,
        action_url=f"/tasks/{task.id}"
    )
    db.add(notification)
    db.commit()
    
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user.role.hierarchy_level == 5:
        if task.assigned_to_id != current_user.id and task.assigned_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this task")
    elif current_user.role.hierarchy_level == 4:
        if not permission_checker.can_access_department(current_user, task.department):
            raise HTTPException(status_code=403, detail="Not authorized to view this task")
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user.role.hierarchy_level == 5 and task.assigned_to_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    update_data = task_in.model_dump(exclude_unset=True)
    
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    if task.assigned_by_id != current_user.id:
        notification = Notification(
            user_id=task.assigned_by_id,
            notification_type=NotificationType.TASK_UPDATED,
            title="Task Updated",
            message=f"Task '{task.title}' has been updated",
            related_entity_type="task",
            related_entity_id=task.id,
            action_url=f"/tasks/{task.id}"
        )
        db.add(notification)
        db.commit()
    
    return task


@router.post("/{task_id}/escalate", response_model=TaskResponse)
def escalate_task(
    task_id: int,
    escalation: TaskEscalate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assigned_to_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only assigned user can escalate task")
    
    task.is_escalated = True
    task.escalation_reason = escalation.escalation_reason
    task.escalated_at = datetime.utcnow()
    task.status = TaskStatus.BLOCKED
    
    db.commit()
    db.refresh(task)
    
    vp_users = db.query(User).filter(User.role_id == 3).all()
    for vp_user in vp_users:
        notification = Notification(
            user_id=vp_user.id,
            notification_type=NotificationType.TASK_ESCALATED,
            title="Task Escalated",
            message=f"Task '{task.title}' has been escalated: {escalation.escalation_reason}",
            related_entity_type="task",
            related_entity_id=task.id,
            action_url=f"/tasks/{task.id}"
        )
        db.add(notification)
    
    notification = Notification(
        user_id=task.assigned_by_id,
        notification_type=NotificationType.TASK_ESCALATED,
        title="Task Escalated",
        message=f"Task '{task.title}' has been escalated by assignee",
        related_entity_type="task",
        related_entity_id=task.id,
        action_url=f"/tasks/{task.id}"
    )
    db.add(notification)
    db.commit()
    
    return task


@router.post("/{task_id}/comments", response_model=TaskCommentResponse)
def add_task_comment(
    task_id: int,
    comment_in: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    comment = TaskComment(
        task_id=task_id,
        user_id=current_user.id,
        comment=comment_in.comment
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).order_by(TaskComment.created_at.desc()).all()
    return comments


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assigned_by_id != current_user.id and current_user.role.hierarchy_level > 3:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    task.status = TaskStatus.CANCELLED
    db.commit()
    
    return {"message": "Task cancelled successfully"}
