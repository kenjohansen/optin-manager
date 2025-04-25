"""
Script to create sample opt-in programs in the database.
This is useful for testing the preferences management functionality.
"""

import os
import sys
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the models
from app.models.optin import OptIn, OptInTypeEnum, OptInStatusEnum
from app.core.database import Base

# Get the database URL from environment or use the default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")
print(f"[DEBUG] Using database URL: {DATABASE_URL}")

# Create an engine that connects to the database
engine = create_engine(DATABASE_URL)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Sample opt-in programs
sample_optins = [
    {
        "id": str(uuid.uuid4()),
        "name": "Marketing Emails",
        "type": OptInTypeEnum.promotional.value,
        "description": "Receive marketing emails about our products and services",
        "status": OptInStatusEnum.active.value
    },
    {
        "id": str(uuid.uuid4()),
        "name": "SMS Notifications",
        "type": OptInTypeEnum.alert.value,
        "description": "Receive SMS notifications about your account and services",
        "status": OptInStatusEnum.active.value
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Newsletter",
        "type": OptInTypeEnum.promotional.value,
        "description": "Receive our monthly newsletter with updates and tips",
        "status": OptInStatusEnum.active.value
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Account Updates",
        "type": OptInTypeEnum.transactional.value,
        "description": "Receive important updates about your account",
        "status": OptInStatusEnum.active.value
    }
]

# Check if we already have opt-in programs
existing_count = session.query(OptIn).count()
if existing_count > 0:
    print(f"[INFO] Found {existing_count} existing opt-in programs. Skipping creation.")
else:
    # Create the opt-in programs
    for optin_data in sample_optins:
        optin = OptIn(**optin_data)
        session.add(optin)
    
    # Commit the changes
    session.commit()
    print(f"[INFO] Created {len(sample_optins)} sample opt-in programs.")

# Print the opt-in programs
optins = session.query(OptIn).all()
print("\nAvailable Opt-In Programs:")
print("=" * 50)
for optin in optins:
    print(f"ID: {optin.id}")
    print(f"Name: {optin.name}")
    print(f"Type: {optin.type}")
    print(f"Description: {optin.description}")
    print(f"Status: {optin.status}")
    print("-" * 50)

# Close the session
session.close()
print("\n[INFO] Done.")
