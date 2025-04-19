import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")

settings = Settings()
