
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/library_db"
    UPLOAD_DIR: str = "uploads"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "default-secret-key-change-in-production"

    def get_cors_origins(self):
        """Get CORS origins for the application"""
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in environment

settings = Settings()