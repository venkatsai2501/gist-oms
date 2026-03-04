from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.role import Role
from app.models.user import User
from app.schemas.user import RoleResponse, RoleBase

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available roles.
    
    Accessible by all authenticated users.
    """
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific role by its ID.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.post("/", response_model=RoleResponse)
def create_role(
    role_in: RoleBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new role.
    
    Only superusers can create roles.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create roles"
        )
    
    # Check if role with same name already exists
    existing_role = db.query(Role).filter(Role.role_name == role_in.role_name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    role = Role(
        role_name=role_in.role_name,
        hierarchy_level=role_in.hierarchy_level,
        description=role_in.description
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
