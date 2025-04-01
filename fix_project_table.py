"""
Script to fix the Project table schema in the database.
This ensures the table has all the required columns.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from enum import Enum as PyEnum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Define ProjectStatus enum
class ProjectStatus(PyEnum):
    """Project status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

def fix_project_table():
    """Fix the Project table schema in the database."""
    logger.info(f"Connecting to database: {DATABASE_URL}")
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we're using PostgreSQL
        if "postgresql" in DATABASE_URL:
            logger.info("PostgreSQL database detected, fixing Project table...")
            
            # Check if the projects table exists
            check_table_sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'projects'
            );
            """
            table_exists = db.execute(text(check_table_sql)).scalar()
            
            if table_exists:
                logger.info("Projects table exists, checking columns...")
                
                # Check if title column exists
                check_column_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'projects' AND column_name = 'title'
                );
                """
                title_exists = db.execute(text(check_column_sql)).scalar()
                
                if not title_exists:
                    logger.info("Title column doesn't exist, adding it...")
                    try:
                        db.execute(text("""
                        ALTER TABLE projects 
                        ADD COLUMN title VARCHAR(255) NOT NULL DEFAULT 'Untitled Project';
                        """))
                        db.commit()
                        logger.info("Added title column to projects table")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Error adding title column: {e}")
                else:
                    logger.info("Title column already exists")
                
                # Check for other required columns and add them if missing
                columns_to_check = [
                    ("description", "TEXT"),
                    ("status", "VARCHAR"),
                    ("client_id", "INTEGER"),
                    ("property_id", "INTEGER"),
                    ("assigned_to", "INTEGER"),
                    ("estimated_value", "FLOAT")
                ]
                
                for col_name, col_type in columns_to_check:
                    check_col_sql = f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = '{col_name}'
                    );
                    """
                    col_exists = db.execute(text(check_col_sql)).scalar()
                    
                    if not col_exists:
                        logger.info(f"{col_name} column doesn't exist, adding it...")
                        try:
                            db.execute(text(f"""
                            ALTER TABLE projects 
                            ADD COLUMN {col_name} {col_type};
                            """))
                            db.commit()
                            logger.info(f"Added {col_name} column to projects table")
                        except Exception as e:
                            db.rollback()
                            logger.error(f"Error adding {col_name} column: {e}")
            else:
                logger.info("Projects table doesn't exist, creating it...")
                
                # Create the projects table with all required columns
                metadata = MetaData()
                
                # First ensure the ProjectStatus enum type exists
                try:
                    db.execute(text("DROP TYPE IF EXISTS projectstatus CASCADE;"))
                    db.execute(text("""
                    CREATE TYPE projectstatus AS ENUM ('draft', 'in_progress', 'review', 'completed', 'archived');
                    """))
                    db.commit()
                    logger.info("Created projectstatus enum type")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error creating projectstatus enum type: {e}")
                
                # Create the projects table
                try:
                    db.execute(text("""
                    CREATE TABLE projects (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL DEFAULT 'Untitled Project',
                        description TEXT,
                        status projectstatus DEFAULT 'draft',
                        client_id INTEGER REFERENCES clients(id),
                        property_id INTEGER REFERENCES properties(id),
                        assigned_to INTEGER REFERENCES users(id),
                        estimated_value FLOAT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    """))
                    db.commit()
                    logger.info("Created projects table with all required columns")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error creating projects table: {e}")
        else:
            logger.info("Not a PostgreSQL database, no fixes needed")
        
        logger.info("Project table fix completed")
    except Exception as e:
        logger.error(f"Error fixing Project table: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_project_table()
