"""User model for the application."""
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
import os

from .base import Base, TimestampMixin

class UserRole(PyEnum):
    """User role enumeration."""
    ADMIN = "ADMIN"
    APPRAISER = "APPRAISER"
    REVIEWER = "REVIEWER"
    CLIENT = "CLIENT"

class User(Base, TimestampMixin):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.APPRAISER)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    assigned_projects = relationship("Project", back_populates="assigned_user")
