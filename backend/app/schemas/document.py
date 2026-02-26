from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.document import DocumentStatus, ApprovalChainType
from app.models.document_approval import ApprovalAction


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: str
    department: str
    approval_chain_type: ApprovalChainType = ApprovalChainType.ROUTINE


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DocumentStatus] = None


class DocumentResponse(DocumentBase):
    id: int
    uploader_id: int
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    status: DocumentStatus
    current_approver_id: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: datetime
    final_approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentApprovalCreate(BaseModel):
    action: ApprovalAction
    comments: Optional[str] = None


class DocumentApprovalResponse(BaseModel):
    id: int
    document_id: int
    approver_id: int
    action: ApprovalAction
    comments: Optional[str] = None
    approval_level: int
    signature_hash: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
