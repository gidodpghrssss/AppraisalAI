"""
Script to fix the UserRole enum in the database.
This ensures the enum type is properly created and values are consistent.
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

def fix_user_role_enum():
    """Fix the UserRole enum in the database."""
    logger.info(f"Connecting to database: {DATABASE_URL}")
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we're using PostgreSQL
        if "postgresql" in DATABASE_URL:
            logger.info("PostgreSQL database detected, fixing UserRole enum...")
            
            # Check if the enum type exists
            check_enum_sql = """
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'userrole'
            );
            """
            result = db.execute(text(check_enum_sql)).scalar()
            
            if result:
                logger.info("UserRole enum type exists, updating values...")
                
                # Drop the enum type constraint
                try:
                    db.execute(text("ALTER TABLE users ALTER COLUMN role DROP DEFAULT;"))
                    db.execute(text("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR;"))
                    db.commit()
                    logger.info("Dropped enum constraint from users table")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error dropping enum constraint: {e}")
                    
                # Drop the enum type
                try:
                    db.execute(text("DROP TYPE IF EXISTS userrole;"))
                    db.commit()
                    logger.info("Dropped userrole enum type")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error dropping enum type: {e}")
            
            # Create the enum type with correct values
            try:
                db.execute(text("""
                CREATE TYPE userrole AS ENUM ('ADMIN', 'APPRAISER', 'REVIEWER', 'CLIENT');
                """))
                db.commit()
                logger.info("Created userrole enum type with correct values")
            except Exception as e:
                db.rollback()
                logger.error(f"Error creating enum type: {e}")
            
            # Update the users table to use the enum type
            try:
                # First update any existing values to match the enum case
                db.execute(text("""
                UPDATE users SET role = UPPER(role) WHERE role IS NOT NULL;
                """))
                
                # Then alter the column to use the enum type
                db.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN role TYPE userrole USING role::userrole;
                """))
                
                # Set the default value
                db.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN role SET DEFAULT 'APPRAISER'::userrole;
                """))
                
                db.commit()
                logger.info("Updated users table to use the enum type")
            except Exception as e:
                db.rollback()
                logger.error(f"Error updating users table: {e}")
        else:
            logger.info("Not a PostgreSQL database, no fixes needed")
        
        logger.info("Database fix completed successfully")
    except Exception as e:
        logger.error(f"Error fixing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_role_enum()
