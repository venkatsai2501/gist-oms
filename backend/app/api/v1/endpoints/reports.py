from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, Integer
from datetime import datetime, timedelta
from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.document import Document, DocumentStatus
from app.models.meeting import Meeting, MeetingStatus

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    hierarchy_level = current_user.role.hierarchy_level
    
    if hierarchy_level == 1:
        return get_director_dashboard(db, current_user)
    elif hierarchy_level == 2:
        return get_principal_dashboard(db, current_user)
    elif hierarchy_level == 3:
        return get_vp_dashboard(db, current_user)
    elif hierarchy_level == 4:
        return get_hod_dashboard(db, current_user)
    else:
        return get_employee_dashboard(db, current_user)


def get_director_dashboard(db: Session, user: User) -> Dict[str, Any]:
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
    escalated_tasks = db.query(Task).filter(Task.is_escalated == True).count()
    
    total_documents = db.query(Document).count()
    pending_documents = db.query(Document).filter(
        Document.status == DocumentStatus.PENDING,
        Document.current_approver_id == user.id
    ).count()
    
    department_stats = db.query(
        Task.department,
        func.count(Task.id).label('total'),
        func.sum(func.cast((Task.status == TaskStatus.COMPLETED), Integer)).label('completed')
    ).filter(Task.department.isnot(None)).group_by(Task.department).all()
    
    return {
        "role": "Director",
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "escalated_tasks": escalated_tasks,
        "task_completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        "total_documents": total_documents,
        "pending_approvals": pending_documents,
        "department_stats": [
            {
                "department": stat[0],
                "total_tasks": stat[1],
                "completed_tasks": stat[2] or 0,
                "completion_rate": round((stat[2] or 0) / stat[1] * 100, 2) if stat[1] > 0 else 0
            }
            for stat in department_stats
        ]
    }


def get_principal_dashboard(db: Session, user: User) -> Dict[str, Any]:
    pending_documents = db.query(Document).filter(
        Document.status == DocumentStatus.PENDING,
        Document.current_approver_id == user.id
    ).count()
    
    total_documents = db.query(Document).count()
    approved_documents = db.query(Document).filter(Document.status == DocumentStatus.APPROVED).count()
    
    total_tasks = db.query(Task).count()
    overdue_tasks = db.query(Task).filter(
        Task.due_date < datetime.utcnow(),
        Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
    ).count()
    
    return {
        "role": "Principal",
        "pending_approvals": pending_documents,
        "total_documents": total_documents,
        "approved_documents": approved_documents,
        "total_tasks": total_tasks,
        "overdue_tasks": overdue_tasks
    }


def get_vp_dashboard(db: Session, user: User) -> Dict[str, Any]:
    total_tasks = db.query(Task).count()
    escalated_tasks = db.query(Task).filter(Task.is_escalated == True).count()
    
    overdue_tasks = db.query(Task).filter(
        Task.due_date < datetime.utcnow(),
        Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
    ).count()
    
    pending_meetings = db.query(Meeting).filter(Meeting.status == MeetingStatus.PENDING).count()
    
    task_by_status = db.query(
        Task.status,
        func.count(Task.id)
    ).group_by(Task.status).all()
    
    return {
        "role": "Vice Principal",
        "total_tasks": total_tasks,
        "escalated_tasks": escalated_tasks,
        "overdue_tasks": overdue_tasks,
        "pending_meetings": pending_meetings,
        "task_by_status": {status.value: count for status, count in task_by_status}
    }


def get_hod_dashboard(db: Session, user: User) -> Dict[str, Any]:
    department_tasks = db.query(Task).filter(Task.department == user.department).count()
    
    completed_tasks = db.query(Task).filter(
        Task.department == user.department,
        Task.status == TaskStatus.COMPLETED
    ).count()
    
    my_team = db.query(User).filter(
        User.department == user.department,
        User.role_id >= user.role_id
    ).count()
    
    pending_documents = db.query(Document).filter(
        Document.department == user.department,
        Document.current_approver_id == user.id
    ).count()
    
    return {
        "role": "HOD",
        "department": user.department or "Unknown",
        "department_tasks": department_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": round((completed_tasks / department_tasks * 100) if department_tasks > 0 else 0, 2),
        "team_size": my_team,
        "pending_approvals": pending_documents
    }


def get_employee_dashboard(db: Session, user: User) -> Dict[str, Any]:
    my_tasks = db.query(Task).filter(Task.assigned_to_id == user.id).count()
    
    completed_tasks = db.query(Task).filter(
        Task.assigned_to_id == user.id,
        Task.status == TaskStatus.COMPLETED
    ).count()
    
    in_progress_tasks = db.query(Task).filter(
        Task.assigned_to_id == user.id,
        Task.status == TaskStatus.IN_PROGRESS
    ).count()
    
    overdue_tasks = db.query(Task).filter(
        Task.assigned_to_id == user.id,
        Task.due_date < datetime.utcnow(),
        Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
    ).count()
    
    my_documents = db.query(Document).filter(Document.uploader_id == user.id).count()
    
    return {
        "role": "Employee",
        "my_tasks": my_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "overdue_tasks": overdue_tasks,
        "my_documents": my_documents
    }


@router.get("/task-completion")
def get_task_completion_report(
    days: int = 30,
    department: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.hierarchy_level > 3 and not department:
        department = current_user.department
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(Task).filter(Task.created_at >= start_date)
    
    if department:
        query = query.filter(Task.department == department)
    
    tasks = query.all()
    
    total = len(tasks)
    completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    in_progress = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
    blocked = len([t for t in tasks if t.status == TaskStatus.BLOCKED])
    
    return {
        "period_days": days,
        "department": department,
        "total_tasks": total,
        "completed": completed,
        "in_progress": in_progress,
        "blocked": blocked,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 2)
    }


@router.get("/approval-timeline")
def get_approval_timeline_report(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.hierarchy_level > 2:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    documents = db.query(Document).filter(
        Document.created_at >= start_date,
        Document.status == DocumentStatus.APPROVED
    ).all()
    
    approval_times = []
    for doc in documents:
        if doc.final_approved_at:
            time_diff = (doc.final_approved_at - doc.created_at).total_seconds() / 3600
            approval_times.append(time_diff)
    
    avg_approval_time = sum(approval_times) / len(approval_times) if approval_times else 0
    
    return {
        "period_days": days,
        "total_approved": len(documents),
        "average_approval_time_hours": round(avg_approval_time, 2),
        "min_approval_time_hours": round(min(approval_times), 2) if approval_times else 0,
        "max_approval_time_hours": round(max(approval_times), 2) if approval_times else 0
    }
