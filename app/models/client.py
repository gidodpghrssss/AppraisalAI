"""Client model for the application."""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class Client(Base, TimestampMixin):
    """Client model."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    company = Column(String(255))
    address = Column(String(255))
    notes = Column(Text)
    
    # Relationships
    projects = relationship("Project", back_populates="client")
