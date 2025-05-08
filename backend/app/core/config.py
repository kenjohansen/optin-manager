"""
core/config.py

Configuration settings for the OptIn Manager backend.

This module provides centralized configuration management for the OptIn Manager system,
loading environment variables and providing default values when needed. It ensures that
the application can be configured via environment variables without code changes.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with fallback defaults.
    
    This class uses Pydantic's BaseSettings to automatically load values from environment
    variables. Each setting has a default value that is used if the corresponding
    environment variable is not set.
    
    As noted in the memories, the backend must support SQLite for development and testing,
    not PostgreSQL. The default DATABASE_URL reflects this requirement.
    
    Attributes:
        DATABASE_URL (str): The database connection string. Defaults to a local SQLite
                          database, which is essential for development and testing
                          as specified in the project requirements.
        
        SECRET_KEY (str): Secret key used for JWT token signing and other security
                        features. Should be changed in production environments.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")

# Create a global settings instance to be imported by other modules
settings = Settings()
