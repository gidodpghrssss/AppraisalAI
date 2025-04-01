"""
One-time script to fix database issues on Render deployment.
This script will be run once during deployment to fix the enum issues.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
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
            
            # Add any other PostgreSQL-specific fixes here
            
        else:
            logger.info("Not a PostgreSQL database, no fixes needed")
        
        logger.info("Database fix completed")
    except Exception as e:
        logger.error(f"Error fixing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_database()
