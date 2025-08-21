from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/library_db")
    LOG_LEVEL: str = "INFO"
    UPLOAD_DIR: str = "uploads"
    
settings = Settings()