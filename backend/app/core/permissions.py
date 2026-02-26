from typing import Optional
from fastapi import HTTPException, status
from app.models.user import User


class PermissionChecker:
    """
    Hierarchical permission checker based on role levels.
    Lower hierarchy_level = Higher authority
    """
    
    @staticmethod
    def check_hierarchy_level(user: User, required_level: int) -> bool:
        """
        Check if user has sufficient hierarchy level.
        Returns True if user.hierarchy_level <= required_level
        """
        return user.role.hierarchy_level <= required_level
    
    @staticmethod
    def require_level(user: User, required_level: int, error_msg: str = None):
        """
        Raise exception if user doesn't have required hierarchy level.
        """
        if not PermissionChecker.check_hierarchy_level(user, required_level):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg or f"Insufficient permissions. Required hierarchy level: {required_level}"
            )
    
    @staticmethod
    def can_view_user(viewer: User, target_user: User) -> bool:
        """
        Higher roles can view lower roles.
        Same level can view each other.
        """
        return viewer.role.hierarchy_level <= target_user.role.hierarchy_level
    
    @staticmethod
    def can_approve_document(approver: User, document_creator: User) -> bool:
        """
        Can only approve documents from lower hierarchy levels.
        """
        return approver.role.hierarchy_level < document_creator.role.hierarchy_level
    
    @staticmethod
    def can_assign_task(assigner: User, assignee: User) -> bool:
        """
        Can assign tasks to same or lower hierarchy levels.
        """
        return assigner.role.hierarchy_level <= assignee.role.hierarchy_level
    
    @staticmethod
    def can_access_department(user: User, department: str) -> bool:
        """
        HOD can only access their department.
        VP and above can access all departments.
        """
        if user.role.hierarchy_level <= 3:  # Director, Principal, VP
            return True
        return user.department == department
    
    @staticmethod
    def can_view_audit_logs(user: User) -> bool:
        """
        Only Director and Admin can view audit logs.
        """
        return user.role.hierarchy_level == 1 or user.role.role_name == "Admin"


def get_permission_checker() -> PermissionChecker:
    return PermissionChecker()
