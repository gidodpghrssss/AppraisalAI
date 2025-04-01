from app.db.session import SessionLocal
from app.models.project import Project
import sqlite3

# Create a database session
db = SessionLocal()

# Check projects in the database
print("Projects in database:")
try:
    projects = db.query(Project).all()
    for p in projects:
        print(f"ID: {p.id}, Title: {p.title}, Status: {p.status}")
except Exception as e:
    print(f"Error querying projects: {e}")

# Connect directly to the SQLite database
print("\nDirect database check:")
try:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status FROM projects")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1]}, Status: {row[2]}")
    conn.close()
except Exception as e:
    print(f"Error with direct database query: {e}")
