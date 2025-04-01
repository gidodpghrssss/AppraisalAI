"""
Script to create an admin user in the database.
This allows access to the admin dashboard.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(email="admin@appraisalai.com", password="Admin123!", full_name="Admin User"):
    """Create an admin user in the database."""
    logger.info(f"Creating admin user with email: {email}")
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if the users table exists
        check_table_sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'users'
        );
        """
        table_exists = db.execute(text(check_table_sql)).scalar()
        
        if not table_exists:
            logger.error("Users table doesn't exist. Please run database migrations first.")
            return
        
        # Check if the user already exists
        check_user_sql = f"""
        SELECT EXISTS (
            SELECT FROM users 
            WHERE email = '{email}'
        );
        """
        user_exists = db.execute(text(check_user_sql)).scalar()
        
        if user_exists:
            logger.info(f"User with email {email} already exists. Updating password.")
            
            # Update the existing user
            hashed_password = pwd_context.hash(password)
            update_user_sql = f"""
            UPDATE users 
            SET hashed_password = '{hashed_password}', 
                full_name = '{full_name}', 
                role = 'ADMIN' 
            WHERE email = '{email}';
            """
            db.execute(text(update_user_sql))
            db.commit()
            logger.info(f"Updated user {email} with admin role and new password")
        else:
            # Create a new admin user
            hashed_password = pwd_context.hash(password)
            create_user_sql = f"""
            INSERT INTO users (email, hashed_password, full_name, role, is_active)
            VALUES ('{email}', '{hashed_password}', '{full_name}', 'ADMIN', true);
            """
            db.execute(text(create_user_sql))
            db.commit()
            logger.info(f"Created new admin user: {email}")
        
        logger.info("Admin user creation/update completed successfully")
        logger.info(f"You can now log in with: {email} / {password}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # You can override the default credentials by passing arguments
    if len(sys.argv) > 1:
        email = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else "Admin123!"
        full_name = sys.argv[3] if len(sys.argv) > 3 else "Admin User"
        create_admin_user(email, password, full_name)
    else:
        create_admin_user()
