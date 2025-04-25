"""
Migration script to update the OptIn model to use string IDs instead of UUIDs.

This script:
1. Creates a backup of the database
2. Updates the OptIn model to use string IDs
3. Updates the database schema to match the new model

Run this script directly with Python to perform the migration.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database connection
DB_PATH = os.getenv("DB_PATH", "./optin_manager.db")

def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    backup_path = f"{DB_PATH}.backup_optin_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Database backed up to: {backup_path}")
    return backup_path

def update_optin_model():
    """Update the OptIn model in app/models/optin.py to use string IDs"""
    optin_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "app", "models", "optin.py")
    
    with open(optin_model_path, "r") as f:
        content = f.read()
    
    # Replace PostgreSQL UUID import with String
    content = content.replace(
        "from sqlalchemy.dialects.postgresql import UUID", 
        "# Use String type for UUID in SQLite\nfrom sqlalchemy import String as UUID"
    )
    
    # Update the id column definition
    content = content.replace(
        "id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)",
        "id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))"
    )
    
    with open(optin_model_path, "w") as f:
        f.write(content)
    
    print(f"Updated OptIn model at {optin_model_path}")

def migrate_optins_table():
    """Migrate optins table to use string IDs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the optins table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='optins'")
    if not cursor.fetchone():
        print("Optins table does not exist. No migration needed.")
        return
    
    print("Starting migration of optins table...")
    
    # Create a temporary table with the new schema
    cursor.execute("""
    CREATE TABLE optins_new (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP
    )
    """)
    
    # Fetch all existing optins
    cursor.execute("SELECT id, name, type, description, status, created_at, updated_at FROM optins")
    optins = cursor.fetchall()
    print(f"Found {len(optins)} optins to migrate")
    
    # Migrate each optin
    for optin in optins:
        old_id, name, type_, description, status, created_at, updated_at = optin
        
        # Convert UUID to string if needed
        if isinstance(old_id, bytes) or (isinstance(old_id, str) and '-' in old_id):
            # If it's a UUID string with hyphens, remove them
            new_id = str(old_id).replace('-', '')
        else:
            new_id = old_id
        
        # Insert into new table
        cursor.execute("""
        INSERT INTO optins_new (id, name, type, description, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (new_id, name, type_, description, status, created_at, updated_at))
        
        print(f"Migrated optin: {name} ({old_id} -> {new_id})")
    
    # Rename tables to complete the migration
    cursor.execute("DROP TABLE optins")
    cursor.execute("ALTER TABLE optins_new RENAME TO optins")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Migration of optins table completed successfully!")

def update_preferences_api():
    """Update the preferences API to handle string IDs"""
    preferences_api_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                       "app", "api", "preferences.py")
    
    with open(preferences_api_path, "r") as f:
        content = f.read()
    
    # Fix the UUID handling in the API
    if "from uuid import UUID" in content:
        # Replace UUID conversion with string handling
        content = content.replace("program_id = UUID(program_id)", "program_id = str(program_id)")
        
        # Fix any other UUID conversions
        content = content.replace("UUID(", "str(")
    
    with open(preferences_api_path, "w") as f:
        f.write(content)
    
    print(f"Updated preferences API at {preferences_api_path}")

if __name__ == "__main__":
    # Backup the database first
    backup_path = backup_database()
    
    # Confirm before proceeding
    confirm = input(f"Database backed up to {backup_path}. Proceed with migration? (y/n): ")
    if confirm.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Update the OptIn model
    update_optin_model()
    
    # Migrate the optins table
    migrate_optins_table()
    
    # Update the preferences API
    update_preferences_api()
    
    print("Migration completed successfully!")
