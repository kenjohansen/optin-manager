"""
Script to create the consents table in the database.

This script should be run directly to create the consents table
if it doesn't already exist in the database.
"""

import os
import sys
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.sqlite import DATETIME as sqlite_datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the Base class from the database module
from app.core.database import Base, get_db
from app.models.consent import Consent, ConsentStatusEnum, ConsentChannelEnum

# Get the database URL from environment or use the default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")

# Create an engine that connects to the database
engine = create_engine(DATABASE_URL)

# Create the table
Base.metadata.create_all(engine, tables=[Consent.__table__])

print("Consents table created successfully!")
