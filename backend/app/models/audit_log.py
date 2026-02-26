from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)
    
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    
    details = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", backref="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} on {self.module}>"
