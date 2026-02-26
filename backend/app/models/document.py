from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base import Base


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ApprovalChainType(str, Enum):
    ROUTINE = "routine"
    FINANCIAL = "financial"
    STRATEGIC = "strategic"
    CUSTOM = "custom"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(String(100), nullable=False)
    
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)
    
    approval_chain_type = Column(SQLEnum(ApprovalChainType), default=ApprovalChainType.ROUTINE, nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False, index=True)
    
    current_approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    final_approved_at = Column(DateTime, nullable=True)
    
    uploader = relationship("User", foreign_keys=[uploader_id], backref="uploaded_documents")
    current_approver = relationship("User", foreign_keys=[current_approver_id], backref="pending_approvals")
    
    def __repr__(self):
        return f"<Document {self.id}: {self.title} - {self.status}>"
