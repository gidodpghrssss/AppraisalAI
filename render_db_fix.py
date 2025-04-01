"""
One-time script to fix database issues on Render deployment.
This script will be run once during deployment to fix the enum issues.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

def fix_database():
    """Fix database issues for Render deployment."""
    logger.info(f"Starting database fix for Render deployment")
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we're using PostgreSQL
        if "postgresql" in DATABASE_URL:
            logger.info("PostgreSQL database detected")
            
            # Fix UserRole enum
            try:
                # First check if the users table exists
                check_table_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
                """
                table_exists = db.execute(text(check_table_sql)).scalar()
                
                if table_exists:
                    logger.info("Users table exists, fixing enum issues")
                    
                    # Try to update the role column to use uppercase values
                    try:
                        db.execute(text("""
                        ALTER TABLE users ALTER COLUMN role TYPE VARCHAR;
                        UPDATE users SET role = UPPER(role) WHERE role IS NOT NULL;
                        """))
                        db.commit()
                        logger.info("Updated role values to uppercase")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Error updating role values: {e}")
                    
                    # Try to recreate the enum type
                    try:
                        # Drop the existing enum type if it exists
                        db.execute(text("DROP TYPE IF EXISTS userrole CASCADE;"))
                        db.commit()
                        
                        # Create the enum type with correct values
                        db.execute(text("""
                        CREATE TYPE userrole AS ENUM ('ADMIN', 'APPRAISER', 'REVIEWER', 'CLIENT');
                        """))
                        db.commit()
                        
                        # Alter the column to use the enum type
                        db.execute(text("""
                        ALTER TABLE users 
                        ALTER COLUMN role TYPE userrole USING role::userrole;
                        """))
                        db.commit()
                        
                        logger.info("Successfully recreated the userrole enum type")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Error recreating enum type: {e}")
                else:
                    logger.info("Users table doesn't exist yet, no fixes needed")
            except Exception as e:
                logger.error(f"Error fixing UserRole enum: {e}")
            
            # Fix Project table
            try:
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
                    try:
                        # First ensure the ProjectStatus enum type exists
                        db.execute(text("DROP TYPE IF EXISTS projectstatus CASCADE;"))
                        db.execute(text("""
                        CREATE TYPE projectstatus AS ENUM ('draft', 'in_progress', 'review', 'completed', 'archived');
                        """))
                        db.commit()
                        
                        # Create the projects table
                        db.execute(text("""
                        CREATE TABLE projects (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255) NOT NULL DEFAULT 'Untitled Project',
                            description TEXT,
                            status projectstatus DEFAULT 'draft',
                            client_id INTEGER,
                            property_id INTEGER,
                            assigned_to INTEGER,
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
            except Exception as e:
                logger.error(f"Error fixing Project table: {e}")
            
        else:
            logger.info("Not a PostgreSQL database, no fixes needed")
        
        logger.info("Database fix completed")
    except Exception as e:
        logger.error(f"Error fixing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_database()
