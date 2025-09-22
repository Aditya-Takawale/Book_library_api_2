from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import book as book_router
from app.routers import book_enhanced as book_enhanced_router
from app.routers import auth as auth_router
from app.routers import author as author_router
from app.routers import review as review_router
from app.routers import migration as migration_router
from app.routers import loan as loan_router
from app.routers import borrow as borrow_router
from app.routers import user_management as user_management_router
from app.routers import auth_verify as auth_verify_router  # Add this import
from app.routers import test_auth as test_auth_router  # Add test auth router
from app.routers import secure_test as secure_test_router  # Add secure test router
from app.core.db import engine, Base, test_database_connection
from app.database import SessionLocal
from app.models import RequestLog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import os
import datetime
import json
import re
from logging.handlers import RotatingFileHandler
from app.config import settings

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_level = logging.INFO  # Reduced from DEBUG to prevent excessive logging
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            f"{log_dir}/app_{datetime.datetime.now().strftime('%Y%m%d')}.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BookLibraryAPI")

app = FastAPI(
    title="Book Library Management API",
    description="📚 A comprehensive library management system with JWT authentication, RBAC, and advanced features",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
# Note: Database connection test moved to startup event
# Base.metadata.create_all(bind=engine)  # This will be called after connection test

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and run migrations on startup"""
    try:
        logger.info("🚀 Starting Book Library API v2...")
        
        # Test database connection
        test_database_connection()
        
        # Temporarily disable auto-migrations on Railway to fix restart loop
        # Use direct table creation for faster startup
        logger.info("📋 Creating/verifying database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified successfully")
        
        # Migration system is available via /admin/migration endpoints
        logger.info("� Migrations can be run manually via /admin/migration endpoints")
        
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        logger.error("💡 Check your DATABASE_URL environment variable")
        # Don't raise the exception - let the app start even if DB is not available
        # This allows Railway to show better error messages
        pass

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Shutting down Book Library API v2...")

# Include routers
app.include_router(auth_router.router)  # Authentication & basic user operations
app.include_router(user_management_router.router)  # Enhanced user management with RBAC
app.include_router(book_router.router)
app.include_router(book_enhanced_router.router, prefix="/v2")  # Enhanced book management
app.include_router(author_router.router)
app.include_router(review_router.router)
app.include_router(loan_router.router)  # Loan and reservation management
app.include_router(borrow_router.router)  # Member book borrowing
app.include_router(migration_router.router, prefix="/admin")  # Migration management
app.include_router(auth_verify_router.router)  # Auth verification router
app.include_router(test_auth_router.router)  # Test auth router
app.include_router(secure_test_router.router)  # Secure test router

@app.get("/")
async def root():
    logger.info("Accessed root endpoint")
    return {"message": "Welcome to Book Library Management API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    try:
        # Check database connectivity
        from app.core.db import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Check migration status
        from app.utils.migrations import MigrationManager
        migration_manager = MigrationManager()
        status = migration_manager.check_migration_status()
        
        return {
            "status": "healthy",
            "database": "connected",
            "migrations": {
                "current_revision": status.get("current_revision"),
                "is_up_to_date": status.get("is_up_to_date", False)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def mask_sensitive_data(self, body_text: str) -> str:
        """Mask sensitive data like passwords in request body."""
        try:
            # Try to parse as JSON
            if body_text.strip():
                data = json.loads(body_text)
                
                # Fields to mask
                sensitive_fields = ['password', 'passwd', 'pwd', 'secret', 'token', 'key']
                
                def mask_dict(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key.lower() in sensitive_fields:
                                obj[key] = "*" * min(len(str(value)), 8) if value else "***"
                            elif isinstance(value, (dict, list)):
                                mask_dict(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            if isinstance(item, (dict, list)):
                                mask_dict(item)
                
                mask_dict(data)
                return json.dumps(data)
        except (json.JSONDecodeError, Exception):
            # If not JSON, use regex to mask password-like patterns
            patterns = [
                r'("password"\s*:\s*")[^"]*(")',
                r'("passwd"\s*:\s*")[^"]*(")',
                r'("pwd"\s*:\s*")[^"]*(")',
                r'(password=)[^&\s]*',
                r'(passwd=)[^&\s]*',
                r'(pwd=)[^&\s]*'
            ]
            
            masked_body = body_text
            for pattern in patterns:
                masked_body = re.sub(pattern, r'\1********\2', masked_body, flags=re.IGNORECASE)
            return masked_body
        
        return body_text
    
    async def dispatch(self, request: Request, call_next):
        if request.method.upper() == "POST":
            try:
                # Read the body once and store it
                body_bytes = await request.body()
                
                # Create a new request with the same body for the next handler
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                
                # Replace the request's receive function
                request._receive = receive
                
            except Exception as e:
                logger.error(f"Error reading request body: {e}")
                body_bytes = b""

            response: Response = await call_next(request)

            try:
                db = SessionLocal()
                body_text = body_bytes.decode(errors="ignore")
                masked_body = self.mask_sensitive_data(body_text)
                
                log = RequestLog(
                    method=request.method,
                    path=str(request.url.path),
                    headers=str(dict(request.headers)),
                    body=masked_body,
                    status_code=response.status_code,
                )
                db.add(log)
                db.commit()
            except Exception as e:
                logger.error(f"Error logging request: {e}")
            finally:
                try:
                    db.close()
                except Exception:
                    pass

            return response
        else:
            return await call_next(request)


# app.add_middleware(RequestLoggingMiddleware)