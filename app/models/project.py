"""Project model for the application."""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from .base import Base, TimestampMixin

class ProjectStatus(PyEnum):
    """Project status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Project(Base, TimestampMixin):
    """Project model."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    client_id = Column(Integer, ForeignKey("clients.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    estimated_value = Column(Float)
    
    # Relationships
    client = relationship("Client", back_populates="projects")
    property = relationship("Property", back_populates="projects")
    reports = relationship("Report", back_populates="project")
    assigned_user = relationship("User", back_populates="assigned_projects")
