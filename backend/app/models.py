from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from .database import Base

class Changelog(Base):
    __tablename__ = "changelogs"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    changes = Column(JSON, nullable=False)  # {features: [], bugfixes: [], improvements: [], breaking: []}
    commit_range = Column(String(255), nullable=True)  # e.g., "abc123..def456"
    project_name = Column(String(100), default="default")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published = Column(Boolean, default=True)
