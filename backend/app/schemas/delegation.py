from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DelegationCreate(BaseModel):
    delegate_id: int
    start_date: datetime
    end_date: datetime
    reason: Optional[str] = None


class DelegationResponse(BaseModel):
    id: int
    delegator_id: int
    delegate_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
