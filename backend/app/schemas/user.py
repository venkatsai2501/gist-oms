from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    role_name: str
    hierarchy_level: int
    description: Optional[str] = None


class RoleResponse(RoleBase):
    id: int
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    department: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_id: int


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    role_id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    role: RoleResponse
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
