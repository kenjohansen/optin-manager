"""
Migration script to update the contacts table to use encrypted data.

This script:
1. Creates a backup of the contacts table
2. Adds new columns for encrypted data
3. Migrates existing data to the new format
4. Updates foreign key references

Run this script directly with Python to perform the migration.
"""

import os
import sys
import sqlite3
import uuid
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our encryption utilities
from app.core.encryption import encrypt_pii, generate_deterministic_id

# Database connection
DB_PATH = os.getenv("DB_PATH", "./optin_manager.db")

def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Database backed up to: {backup_path}")
    return backup_path

def migrate_contacts():
    """Migrate contacts table to use encrypted data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the contacts table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
    if not cursor.fetchone():
        print("Contacts table does not exist. No migration needed.")
        return
    
    # Check if we've already migrated
    cursor.execute("PRAGMA table_info(contacts)")
    columns = [col[1] for col in cursor.fetchall()]
    if "encrypted_value" in columns:
        print("Migration has already been applied.")
        return
    
    print("Starting migration of contacts table...")
    
    # Create a temporary table with the new schema
    cursor.execute("""
    CREATE TABLE contacts_new (
        id TEXT PRIMARY KEY,
        encrypted_value TEXT NOT NULL UNIQUE,
        contact_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        status TEXT DEFAULT 'active',
        is_admin BOOLEAN DEFAULT 0,
        is_staff BOOLEAN DEFAULT 0,
        comment TEXT
    )
    """)
    
    # Fetch all existing contacts
    cursor.execute("SELECT id, email, phone, created_at, status, is_admin, is_staff, comment FROM contacts")
    contacts = cursor.fetchall()
    print(f"Found {len(contacts)} contacts to migrate")
    
    # Migrate each contact
    for contact in contacts:
        old_id, email, phone, created_at, status, is_admin, is_staff, comment = contact
        
        # Determine contact type and value
        if email:
            contact_type = "email"
            contact_value = email
        elif phone:
            contact_type = "phone"
            contact_value = phone
        else:
            print(f"Skipping contact with no email or phone: {old_id}")
            continue
        
        # Generate deterministic ID and encrypt the contact value
        new_id = generate_deterministic_id(contact_value)
        encrypted_value = encrypt_pii(contact_value)
        
        # Convert string boolean values to integers
        is_admin_bool = 1 if is_admin == "true" else 0
        is_staff_bool = 1 if is_staff == "true" else 0
        
        # Insert into new table
        cursor.execute("""
        INSERT INTO contacts_new (id, encrypted_value, contact_type, created_at, status, is_admin, is_staff, comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_id, encrypted_value, contact_type, created_at, status, is_admin_bool, is_staff_bool, comment))
        
        print(f"Migrated contact: {contact_value} -> ID: {new_id}")
    
    # Update foreign key references in other tables
    migrate_foreign_keys(cursor, contacts)
    
    # Rename tables to complete the migration
    cursor.execute("DROP TABLE contacts")
    cursor.execute("ALTER TABLE contacts_new RENAME TO contacts")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Migration completed successfully!")

def migrate_foreign_keys(cursor, contacts):
    """Update foreign key references to contacts table"""
    
    # Map old UUIDs to new deterministic IDs
    id_mapping = {}
    for contact in contacts:
        old_id, email, phone = contact[0], contact[1], contact[2]
        contact_value = email if email else phone
        if contact_value:
            new_id = generate_deterministic_id(contact_value)
            id_mapping[old_id] = new_id
    
    # Update verification_codes table
    try:
        cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='verification_codes'")
        if cursor.fetchone():
            cursor.execute("SELECT id, user_id FROM verification_codes")
            codes = cursor.fetchall()
            
            for code_id, user_id in codes:
                if user_id in id_mapping:
                    cursor.execute(
                        "UPDATE verification_codes SET user_id = ? WHERE id = ?",
                        (id_mapping[user_id], code_id)
                    )
            print(f"Updated {len(codes)} verification codes")
    except Exception as e:
        print(f"Error updating verification_codes: {str(e)}")
    
    # Update consents table
    try:
        cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='consents'")
        if cursor.fetchone():
            cursor.execute("SELECT id, user_id FROM consents")
            consents = cursor.fetchall()
            
            for consent_id, user_id in consents:
                if user_id in id_mapping:
                    cursor.execute(
                        "UPDATE consents SET user_id = ? WHERE id = ?",
                        (id_mapping[user_id], consent_id)
                    )
            print(f"Updated {len(consents)} consent records")
    except Exception as e:
        print(f"Error updating consents: {str(e)}")

if __name__ == "__main__":
    # Backup the database first
    backup_path = backup_database()
    
    # Confirm before proceeding
    confirm = input(f"Database backed up to {backup_path}. Proceed with migration? (y/n): ")
    if confirm.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Run the migration
    migrate_contacts()
