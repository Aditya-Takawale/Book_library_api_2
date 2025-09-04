
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger("BookLibraryAPI")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

try:
    # MySQL-specific configuration for better performance and compatibility
    engine = create_engine(
        settings.DATABASE_URL,
        # Connection pooling settings
        pool_pre_ping=True,          # Test connections before use
        pool_recycle=3600,           # Recycle connections every hour
        pool_size=5,                 # Number of connections to maintain
        max_overflow=10,             # Additional connections allowed
        pool_timeout=30,             # Timeout for getting connection from pool
        
        # MySQL-specific connection arguments
        connect_args={
            "connect_timeout": 60,   # Connection timeout in seconds
            "read_timeout": 60,      # Read timeout
            "write_timeout": 60,     # Write timeout
            "charset": "utf8mb4",    # Support for full UTF-8
            "use_unicode": True,     # Enable Unicode support
            "autocommit": False,     # Disable autocommit for transactions
        },
        
        # Logging and debugging
        echo=False,                  # Set to True for SQL query debugging
        echo_pool=False,            # Set to True for connection pool debugging
        
        # Performance settings
        isolation_level="READ_COMMITTED",  # Transaction isolation level
    )
    
    Base = declarative_base()

    # Test connection and create database if it doesn't exist
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT 1")).scalar()
            
            # Check if our database exists, create if not
            conn.execute(text("CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.execute(text("USE library_db"))
            
            logger.info("✅ Database connection established successfully")
            logger.info(f"✅ Connected to MySQL at: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")
            
    except Exception as conn_error:
        logger.error(f"❌ Database connection test failed: {str(conn_error)}")
        raise
        
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {str(e)}")
    raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()