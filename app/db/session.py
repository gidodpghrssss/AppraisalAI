"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create database engine with proper settings for PostgreSQL
engine_args = {"pool_pre_ping": True}

# Handle SQLite vs PostgreSQL connection
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False},
        **engine_args
    )
    logger.info("Using SQLite database")
else:
    # For PostgreSQL, we don't need check_same_thread
    engine = create_engine(settings.DATABASE_URL, **engine_args)
    logger.info("Using PostgreSQL database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
