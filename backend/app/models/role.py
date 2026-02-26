from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False, index=True)
    hierarchy_level = Column(Integer, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Role {self.role_name} (Level {self.hierarchy_level})>"
