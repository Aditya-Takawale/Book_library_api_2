
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/library_db"
    UPLOAD_DIR: str = "uploads"
    LOG_LEVEL: str = "INFO"
    # Generate a secure secret key if not provided in environment
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    
    # Production security settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def __post_init__(self):
        """Validate configuration on startup"""
        if self.SECRET_KEY == "default-secret-key-change-in-production":
            print("⚠️  WARNING: Using default SECRET_KEY! Set SECRET_KEY environment variable in production!")
            
        if "root:@" in self.DATABASE_URL:
            print("⚠️  WARNING: Using empty password for database! Set proper DATABASE_URL in production!")

settings = Settings()