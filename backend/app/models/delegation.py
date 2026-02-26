from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Delegation(Base):
    __tablename__ = "delegations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    delegator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delegate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    is_active = Column(Boolean, default=True)
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    delegator = relationship("User", foreign_keys=[delegator_id], backref="delegations_given")
    delegate = relationship("User", foreign_keys=[delegate_id], backref="delegations_received")
    
    def __repr__(self):
        return f"<Delegation {self.delegator_id} -> {self.delegate_id}>"
