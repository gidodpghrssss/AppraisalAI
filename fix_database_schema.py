"""
Script to fix database schema issues in the Render deployment.
This script adds missing columns and fixes type mismatches in the database.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

def fix_database_schema():
    """Fix database schema issues for Render deployment."""
    logger.info(f"Starting database schema fix for Render deployment")
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we're using PostgreSQL
        if "postgresql" in DATABASE_URL:
            logger.info("PostgreSQL database detected")
            
            # Fix projects table
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
                    logger.info("Projects table exists, checking for missing columns")
                    
                    # Check if title column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = 'title'
                    );
                    """
                    title_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not title_exists:
                        logger.info("Adding title column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN title VARCHAR(255);"))
                        db.commit()
                    
                    # Check if description column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = 'description'
                    );
                    """
                    description_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not description_exists:
                        logger.info("Adding description column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN description TEXT;"))
                        db.commit()
                    
                    # Check if client_id column exists and fix its type
                    check_column_sql = """
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = 'projects' AND column_name = 'client_id';
                    """
                    result = db.execute(text(check_column_sql)).fetchone()
                    
                    if result:
                        data_type = result[0]
                        logger.info(f"client_id column exists with type: {data_type}")
                        
                        if data_type == 'character varying':
                            logger.info("Converting client_id from VARCHAR to INTEGER")
                            # Create a temporary column
                            db.execute(text("ALTER TABLE projects ADD COLUMN client_id_temp INTEGER;"))
                            # Try to convert existing values
                            db.execute(text("UPDATE projects SET client_id_temp = client_id::INTEGER WHERE client_id ~ '^[0-9]+$';"))
                            # Drop the old column
                            db.execute(text("ALTER TABLE projects DROP COLUMN client_id;"))
                            # Rename the temp column
                            db.execute(text("ALTER TABLE projects RENAME COLUMN client_id_temp TO client_id;"))
                            db.commit()
                    else:
                        logger.info("Adding client_id column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN client_id INTEGER;"))
                        db.commit()
                    
                    # Check if property_id column exists and fix its type
                    check_column_sql = """
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = 'projects' AND column_name = 'property_id';
                    """
                    result = db.execute(text(check_column_sql)).fetchone()
                    
                    if result:
                        data_type = result[0]
                        logger.info(f"property_id column exists with type: {data_type}")
                        
                        if data_type == 'character varying':
                            logger.info("Converting property_id from VARCHAR to INTEGER")
                            # Create a temporary column
                            db.execute(text("ALTER TABLE projects ADD COLUMN property_id_temp INTEGER;"))
                            # Try to convert existing values
                            db.execute(text("UPDATE projects SET property_id_temp = property_id::INTEGER WHERE property_id ~ '^[0-9]+$';"))
                            # Drop the old column
                            db.execute(text("ALTER TABLE projects DROP COLUMN property_id;"))
                            # Rename the temp column
                            db.execute(text("ALTER TABLE projects RENAME COLUMN property_id_temp TO property_id;"))
                            db.commit()
                    else:
                        logger.info("Adding property_id column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN property_id INTEGER;"))
                        db.commit()
                    
                    # Check if created_at column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = 'created_at'
                    );
                    """
                    created_at_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not created_at_exists:
                        logger.info("Adding created_at column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
                        db.commit()
                    
                    # Check if updated_at column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = 'updated_at'
                    );
                    """
                    updated_at_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not updated_at_exists:
                        logger.info("Adding updated_at column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
                        db.commit()
                    
                    # Check if estimated_value column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = 'estimated_value'
                    );
                    """
                    estimated_value_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not estimated_value_exists:
                        logger.info("Adding estimated_value column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN estimated_value FLOAT;"))
                        db.commit()
                    
                    # Check if assigned_to column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = 'assigned_to'
                    );
                    """
                    assigned_to_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not assigned_to_exists:
                        logger.info("Adding assigned_to column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN assigned_to INTEGER;"))
                        db.commit()
                    
                    # Check if status column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'projects' AND column_name = 'status'
                    );
                    """
                    status_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not status_exists:
                        logger.info("Adding status column to projects table")
                        db.execute(text("ALTER TABLE projects ADD COLUMN status VARCHAR(20) DEFAULT 'DRAFT';"))
                        db.commit()
                else:
                    logger.info("Projects table doesn't exist, creating it")
                    db.execute(text("""
                    CREATE TABLE projects (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255),
                        description TEXT,
                        status VARCHAR(20) DEFAULT 'DRAFT',
                        client_id INTEGER,
                        property_id INTEGER,
                        assigned_to INTEGER,
                        estimated_value FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """))
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Error fixing projects table: {e}")
            
            # Fix clients table
            try:
                # Check if the clients table exists
                check_table_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'clients'
                );
                """
                table_exists = db.execute(text(check_table_sql)).scalar()
                
                if table_exists:
                    logger.info("Clients table exists, checking for missing columns")
                    
                    # Check if name column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'clients' AND column_name = 'name'
                    );
                    """
                    name_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not name_exists:
                        logger.info("Adding name column to clients table")
                        db.execute(text("ALTER TABLE clients ADD COLUMN name VARCHAR(255);"))
                        db.commit()
                    
                    # Check if created_at column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'clients' AND column_name = 'created_at'
                    );
                    """
                    created_at_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not created_at_exists:
                        logger.info("Adding created_at column to clients table")
                        db.execute(text("ALTER TABLE clients ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
                        db.commit()
                else:
                    logger.info("Clients table doesn't exist, creating it")
                    db.execute(text("""
                    CREATE TABLE clients (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        email VARCHAR(255),
                        phone VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """))
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Error fixing clients table: {e}")
            
            # Fix properties table
            try:
                # Check if the properties table exists
                check_table_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'properties'
                );
                """
                table_exists = db.execute(text(check_table_sql)).scalar()
                
                if table_exists:
                    logger.info("Properties table exists, checking for missing columns")
                    
                    # Check if address column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'properties' AND column_name = 'address'
                    );
                    """
                    address_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not address_exists:
                        logger.info("Adding address column to properties table")
                        db.execute(text("ALTER TABLE properties ADD COLUMN address VARCHAR(255);"))
                        db.commit()
                    
                    # Check if city column exists
                    check_column_sql = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'properties' AND column_name = 'city'
                    );
                    """
                    city_exists = db.execute(text(check_column_sql)).scalar()
                    
                    if not city_exists:
                        logger.info("Adding city column to properties table")
                        db.execute(text("ALTER TABLE properties ADD COLUMN city VARCHAR(100);"))
                        db.commit()
                else:
                    logger.info("Properties table doesn't exist, creating it")
                    db.execute(text("""
                    CREATE TABLE properties (
                        id SERIAL PRIMARY KEY,
                        address VARCHAR(255),
                        city VARCHAR(100),
                        state VARCHAR(50),
                        zip VARCHAR(20),
                        property_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """))
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Error fixing properties table: {e}")
        else:
            logger.info("Not using PostgreSQL, no fixes needed")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing database schema: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        logger.info("Database schema fix completed successfully")
        sys.exit(0)
    else:
        logger.error("Database schema fix failed")
        sys.exit(1)
