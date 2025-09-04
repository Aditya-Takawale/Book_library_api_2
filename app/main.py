
from fastapi import FastAPI
from app.routers import book as book_router
from app.routers import book_enhanced as book_enhanced_router
from app.routers import auth as auth_router
from app.routers import author as author_router
from app.routers import review as review_router
from app.routers import migration as migration_router
from app.routers import loan as loan_router
from app.routers import user_management as user_management_router
from app.core.db import engine, Base
from app.database import SessionLocal
from app.models import RequestLog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import os
import datetime
from logging.handlers import RotatingFileHandler
from app.config import settings

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
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

app = FastAPI(title="Book Library Management API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_router.router)  # Authentication & basic user operations
app.include_router(user_management_router.router)  # Enhanced user management with RBAC
app.include_router(book_router.router)
app.include_router(book_enhanced_router.router, prefix="/v2")  # Enhanced book management
app.include_router(author_router.router)
app.include_router(review_router.router)
app.include_router(loan_router.router)  # Loan and reservation management
app.include_router(migration_router.router, prefix="/admin")  # Migration management

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
    async def dispatch(self, request: Request, call_next):
        if request.method.upper() == "POST":
            try:
                body_bytes = await request.body()
                # Reconstruct request stream for downstream handlers
                request._body = body_bytes
            except Exception:
                body_bytes = b""

            response: Response = await call_next(request)

            try:
                db = SessionLocal()
                log = RequestLog(
                    method=request.method,
                    path=str(request.url.path),
                    headers=str(dict(request.headers)),
                    body=body_bytes.decode(errors="ignore"),
                    status_code=response.status_code,
                )
                db.add(log)
                db.commit()
            except Exception:
                pass
            finally:
                try:
                    db.close()
                except Exception:
                    pass

            return response
        else:
            return await call_next(request)


app.add_middleware(RequestLoggingMiddleware)