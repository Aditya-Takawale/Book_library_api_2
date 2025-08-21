
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
import logging

logger = logging.getLogger("BookLibraryAPI")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

try:
    # For MySQL, enable pooling and ping to avoid stale connections
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=280,
    )
    Base = declarative_base()
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise