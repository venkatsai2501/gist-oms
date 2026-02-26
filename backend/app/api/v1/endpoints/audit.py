from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.api.deps import get_db, get_current_active_user, require_director
from app.core.permissions import PermissionChecker
from app.models.audit_log import AuditLog
from app.models.user import User

router = APIRouter()
permission_checker = PermissionChecker()


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    module: str,
    entity_type: str = None,
    entity_id: int = None,
    details: str = None,
    changes: dict = None,
    ip_address: str = None,
    user_agent: str = None
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
    return audit_log


@router.get("/")
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    module: str = None,
    action: str = None,
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_director)
):
    if not permission_checker.can_view_audit_logs(current_user):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view audit logs")
    
    query = db.query(AuditLog)
    
    if module:
        query = query.filter(AuditLog.module == module)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "module": log.module,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "changes": log.changes,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }


@router.get("/user/{user_id}")
def get_user_audit_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_director)
):
    if not permission_checker.can_view_audit_logs(current_user):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view audit logs")
    
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "user_id": user_id,
        "total": db.query(AuditLog).filter(AuditLog.user_id == user_id).count(),
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "module": log.module,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }


@router.get("/stats")
def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_director)
):
    if not permission_checker.can_view_audit_logs(current_user):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view audit logs")
    
    from sqlalchemy import func
    
    total_logs = db.query(AuditLog).count()
    
    by_module = db.query(
        AuditLog.module,
        func.count(AuditLog.id)
    ).group_by(AuditLog.module).all()
    
    by_action = db.query(
        AuditLog.action,
        func.count(AuditLog.id)
    ).group_by(AuditLog.action).all()
    
    return {
        "total_logs": total_logs,
        "by_module": {module: count for module, count in by_module},
        "by_action": {action: count for action, count in by_action}
    }
