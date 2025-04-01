"""
Script to deploy database fixes to Render.
This script adds a migration step to the application startup to fix database issues.
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_main_file():
    """Update main.py to include database migration on startup."""
    logger.info("Updating main.py to include database migration on startup")
    
    main_file_path = "app/main.py"
    
    try:
        with open(main_file_path, "r") as file:
            content = file.read()
        
        # Check if migration code is already added
        if "# Run database migrations" in content:
            logger.info("Migration code already exists in main.py")
            return True
        
        # Find the position to insert migration code (after database initialization)
        if "# Initialize database" in content:
            # Split the content at the database initialization point
            parts = content.split("# Initialize database")
            
            # Find where to insert the migration code (after database initialization)
            if "logger.info(\"Database initialized successfully.\")" in parts[1]:
                # Split at the log message
                init_parts = parts[1].split("logger.info(\"Database initialized successfully.\")")
                
                # Create the new content with migration code
                new_content = parts[0] + "# Initialize database" + init_parts[0] + "logger.info(\"Database initialized successfully.\")"
                
                # Add migration code
                new_content += """

# Run database migrations
logger.info("Running database migrations...")
try:
    from sqlalchemy import text
    
    # Check if we're using PostgreSQL
    if "postgresql" in DATABASE_URL:
        logger.info("PostgreSQL database detected, checking for schema issues")
        
        # Fix projects table schema issues
        try:
            # Check if title column exists
            check_column_sql = \"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'projects' AND column_name = 'title'
            );
            \"\"\"
            title_exists = db.execute(text(check_column_sql)).scalar()
            
            if not title_exists:
                logger.info("Adding title column to projects table")
                db.execute(text("ALTER TABLE projects ADD COLUMN title VARCHAR(255);"))
                db.commit()
            
            # Check if client_id column type
            check_column_sql = \"\"\"
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'client_id';
            \"\"\"
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
            
            # Check if property_id column type
            check_column_sql = \"\"\"
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'property_id';
            \"\"\"
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
            
            logger.info("Database migration completed successfully")
        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            db.rollback()
except Exception as e:
    logger.error(f"Failed to run database migrations: {e}")

"""
                
                # Add the rest of the content
                new_content += init_parts[1]
                
                # Write the updated content back to the file
                with open(main_file_path, "w") as file:
                    file.write(new_content)
                
                logger.info("Successfully updated main.py with migration code")
                return True
            else:
                logger.error("Could not find database initialization log message in main.py")
                return False
        else:
            logger.error("Could not find database initialization section in main.py")
            return False
    except Exception as e:
        logger.error(f"Error updating main.py: {e}")
        return False

def update_models_file():
    """Update models.py to ensure correct column types."""
    logger.info("Updating models.py to ensure correct column types")
    
    models_file_path = "app/models/project.py"
    
    try:
        # Check if the models file exists
        if not os.path.exists(models_file_path):
            logger.error(f"Models file not found at {models_file_path}")
            return False
        
        with open(models_file_path, "r") as file:
            content = file.read()
        
        # Check if Project model has correct column types
        if "class Project" in content:
            # Check if client_id and property_id are defined as Integer
            if "client_id = Column(String" in content:
                content = content.replace("client_id = Column(String", "client_id = Column(Integer")
                logger.info("Updated client_id column type to Integer")
            
            if "property_id = Column(String" in content:
                content = content.replace("property_id = Column(String", "property_id = Column(Integer")
                logger.info("Updated property_id column type to Integer")
            
            # Write the updated content back to the file
            with open(models_file_path, "w") as file:
                file.write(content)
            
            logger.info("Successfully updated models.py with correct column types")
            return True
        else:
            logger.error("Could not find Project model in models.py")
            return False
    except Exception as e:
        logger.error(f"Error updating models.py: {e}")
        return False

def commit_and_push_changes():
    """Commit and push changes to GitHub to trigger Render deployment."""
    logger.info("Committing and pushing changes to GitHub")
    
    try:
        # Add files to git
        files_to_add = ["app/main.py", "fix_database_schema.py", "fix_and_test.py"]
        
        # Add project model file if it exists
        if os.path.exists("app/models/project.py"):
            files_to_add.append("app/models/project.py")
        
        # Add all files
        subprocess.run(["git", "add"] + files_to_add, check=True)
        
        # Commit changes
        subprocess.run(["git", "commit", "-m", "Fix database schema issues for Render deployment"], check=True)
        
        # Push changes to GitHub
        subprocess.run(["git", "push"], check=True)
        
        logger.info("Successfully pushed changes to GitHub")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during git operations: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def run_command(command):
    """Run a shell command and print the output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Output: {result.stdout}")
    return True

def main():
    """Main function to deploy to Render"""
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Update main.py to include database migration
    main_updated = update_main_file()
    
    if not main_updated:
        logger.error("Failed to update main.py")
        return False
    
    # Update models.py to ensure correct column types
    models_updated = update_models_file()
    
    if not models_updated:
        logger.warning("Failed to update models.py, continuing anyway")
    
    # Add all changes
    if not run_command("git add ."):
        print("Failed to add files to git")
        return
    
    # Commit changes
    commit_message = "Fix database schema issues and controller functions for appraisals and analytics"
    if not run_command(f'git commit -m "{commit_message}"'):
        print("Failed to commit changes")
        return
    
    # Push to GitHub
    if not run_command("git push"):
        print("Failed to push to GitHub")
        return
    
    print("Successfully pushed changes to GitHub. Render will automatically deploy the new version.")
    print("You can check the deployment status on the Render dashboard.")

if __name__ == "__main__":
    main()
