"""
Migration script to update the verification_codes table to work with the new encrypted contact model.

This script:
1. Creates a backup of the database
2. Updates the verification_codes table to use string IDs instead of UUIDs
3. Updates foreign key references to match the new contact IDs

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
    backup_path = f"{DB_PATH}.backup_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Database backed up to: {backup_path}")
    return backup_path

def migrate_verification_codes():
    """Migrate verification_codes table to use string IDs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the verification_codes table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='verification_codes'")
    if not cursor.fetchone():
        print("Verification_codes table does not exist. No migration needed.")
        return
    
    print("Starting migration of verification_codes table...")
    
    # Create a temporary table with the new schema
    cursor.execute("""
    CREATE TABLE verification_codes_new (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        code TEXT NOT NULL,
        channel TEXT,
        sent_to TEXT,
        expires_at TIMESTAMP NOT NULL,
        verified_at TIMESTAMP,
        purpose TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES contacts(id)
    )
    """)
    
    # Fetch all existing verification codes
    cursor.execute("SELECT id, user_id, code, channel, sent_to, expires_at, verified_at, purpose, status FROM verification_codes")
    codes = cursor.fetchall()
    print(f"Found {len(codes)} verification codes to migrate")
    
    # Get a mapping of old contact UUIDs to new deterministic IDs
    cursor.execute("SELECT id FROM contacts")
    contact_ids = cursor.fetchall()
    contact_ids = [id[0] for id in contact_ids]
    print(f"Found {len(contact_ids)} contact IDs")
    
    # Migrate each verification code
    for code in codes:
        old_id, user_id, code_value, channel, sent_to, expires_at, verified_at, purpose, status = code
        
        # Convert UUIDs to strings (remove hyphens if present)
        new_id = str(old_id).replace('-', '')
        
        # Check if the user_id exists in the contacts table
        cursor.execute("SELECT id FROM contacts WHERE id = ?", (user_id,))
        contact = cursor.fetchone()
        
        if not contact:
            print(f"Warning: Contact ID {user_id} not found in contacts table. Skipping verification code {old_id}")
            continue
        
        # Insert into new table
        cursor.execute("""
        INSERT INTO verification_codes_new (id, user_id, code, channel, sent_to, expires_at, verified_at, purpose, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_id, user_id, code_value, channel, sent_to, expires_at, verified_at, purpose, status))
        
        print(f"Migrated verification code: {old_id} -> {new_id}")
    
    # Rename tables to complete the migration
    cursor.execute("DROP TABLE verification_codes")
    cursor.execute("ALTER TABLE verification_codes_new RENAME TO verification_codes")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    # Backup the database first
    backup_path = backup_database()
    
    # Confirm before proceeding
    confirm = input(f"Database backed up to {backup_path}. Proceed with migration? (y/n): ")
    if confirm.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Run the migration
    migrate_verification_codes()
