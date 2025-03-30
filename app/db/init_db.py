"""
Database initialization script.
This script creates all necessary database tables on application startup.
"""
import logging
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base
from app.db.session import engine
from app.models.base import *  # Import all models to ensure they're registered with Base

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise

if __name__ == "__main__":
    init_db()
