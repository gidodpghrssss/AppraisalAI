"""Property model for the application."""
from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class Property(Base, TimestampMixin):
    """Property model."""
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    property_type = Column(String(50), nullable=False)
    square_feet = Column(Float)
    lot_size = Column(Float)
    year_built = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    description = Column(Text)
    features = Column(JSON)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    projects = relationship("Project", back_populates="property")
    images = relationship("PropertyImage", back_populates="property")


class PropertyImage(Base, TimestampMixin):
    """Property image model."""
    __tablename__ = "property_images"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(255), nullable=False)
    caption = Column(String(255))
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    property = relationship("Property", back_populates="images")

    def __repr__(self):
        return f"<PropertyImage(id={self.id}, property_id={self.property_id})>"
