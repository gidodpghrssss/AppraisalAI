from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Appraisal(Base):
    __tablename__ = "appraisals"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String, index=True)
    type = Column(String)  # residential, commercial, etc.
    status = Column(String)  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="appraisals")
    
    # Analysis data
    market_analysis = Column(String)
    cost_analysis = Column(String)
    income_analysis = Column(String)
    
    # Value estimates
    market_value = Column(Integer)
    cost_value = Column(Integer)
    income_value = Column(Integer)
    final_value = Column(Integer)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    client_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appraisals = relationship("Appraisal", back_populates="project")
    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    description = Column(String)
    status = Column(String)
    due_date = Column(DateTime)
    assigned_to = Column(String)
    priority = Column(String)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    appraisal_id = Column(Integer, ForeignKey("appraisals.id"))
    title = Column(String)
    content = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appraisal = relationship("Appraisal", back_populates="reports")
