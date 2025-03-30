"""
SQLAlchemy Base class for all models.
Import all models here to ensure they are registered with the Base class.
"""
from sqlalchemy.ext.declarative import declarative_base

# Create declarative base
Base = declarative_base()
