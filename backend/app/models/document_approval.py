from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Enum as SQLEnum, String
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base import Base


class ApprovalAction(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class DocumentApproval(Base):
    __tablename__ = "document_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    action = Column(SQLEnum(ApprovalAction), nullable=False)
    comments = Column(Text, nullable=True)
    
    approval_level = Column(Integer, nullable=False)
    signature_hash = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", backref="approvals")
    approver = relationship("User", backref="document_approvals")
    
    def __repr__(self):
        return f"<DocumentApproval {self.id}: Doc {self.document_id} - {self.action}>"
