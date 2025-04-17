import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/optin_manager")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")

settings = Settings()
