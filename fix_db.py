import sqlite3

# Connect directly to the SQLite database
print("Updating project status values in the database:")
try:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Update 'in_progress' to 'IN_PROGRESS'
    cursor.execute("UPDATE projects SET status = 'IN_PROGRESS' WHERE status = 'in_progress'")
    in_progress_count = cursor.rowcount
    print(f"Updated {in_progress_count} projects from 'in_progress' to 'IN_PROGRESS'")
    
    # Update 'completed' to 'COMPLETED'
    cursor.execute("UPDATE projects SET status = 'COMPLETED' WHERE status = 'completed'")
    completed_count = cursor.rowcount
    print(f"Updated {completed_count} projects from 'completed' to 'COMPLETED'")
    
    # Update 'pending' to 'DRAFT'
    cursor.execute("UPDATE projects SET status = 'DRAFT' WHERE status = 'pending'")
    pending_count = cursor.rowcount
    print(f"Updated {pending_count} projects from 'pending' to 'DRAFT'")
    
    # Commit the changes
    conn.commit()
    
    # Verify the updates
    cursor.execute("SELECT id, title, status FROM projects")
    rows = cursor.fetchall()
    print("\nVerification - Projects after update:")
    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1]}, Status: {row[2]}")
    
    conn.close()
    print("\nDatabase update completed successfully!")
except Exception as e:
    print(f"Error updating database: {e}")
