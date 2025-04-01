"""Report model for the application."""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from .base import Base, TimestampMixin

class ReportStatus(PyEnum):
    """Report status enumeration."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    FINAL = "final"

class Report(Base, TimestampMixin):
    """Report model."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String(255), nullable=False)
    content = Column(Text)
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT)
    report_metadata = Column(JSON)
    version = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey("users.id"))
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    project = relationship("Project", back_populates="reports")
    author = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
