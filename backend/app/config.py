
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

class Settings(BaseSettings):
    # Use Railway DATABASE_URL if available, otherwise fallback to localhost
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/library_db")
    UPLOAD_DIR: str = "uploads"
    LOG_LEVEL: str = "INFO"
    # Generate a secure secret key if not provided in environment
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    
    # Production security settings - include Railway domains and Vercel
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        # Railway domains
        "https://*.railway.app",
        "https://f0f5067f-b62e-4c39-a056-378ee7ee8fd1.railway.app",
        # Render domains
        "https://*.render.com",
        "https://*.onrender.com",
        # Vercel domains
        "https://*.vercel.app",
        "https://*.vercel.com",
        # Add your specific Vercel URL here when you know it
        "https://book-library-frontend.vercel.app"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def __post_init__(self):
        """Validate configuration on startup"""
        if self.SECRET_KEY == "default-secret-key-change-in-production":
            print("⚠️  WARNING: Using default SECRET_KEY! Set SECRET_KEY environment variable in production!")
            
        if "root:@" in self.DATABASE_URL and not os.getenv("RAILWAY_ENVIRONMENT"):
            print("⚠️  WARNING: Using empty password for database! Set proper DATABASE_URL in production!")
            
        # Railway deployment detection
        if os.getenv("RAILWAY_ENVIRONMENT"):
            print(f"🚆 Running on Railway environment: {os.getenv('RAILWAY_ENVIRONMENT')}")
            print(f"🗄️  Database host: {self.DATABASE_URL.split('@')[1].split('/')[0] if '@' in self.DATABASE_URL else 'localhost'}")
            
        # Render deployment detection
        if os.getenv("RENDER"):
            print(f"🎨 Running on Render environment")
            print(f"🗄️  Database host: {self.DATABASE_URL.split('@')[1].split('/')[0] if '@' in self.DATABASE_URL else 'localhost'}")

settings = Settings()