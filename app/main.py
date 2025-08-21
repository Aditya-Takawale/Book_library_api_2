
from fastapi import FastAPI
from app.routers import book as book_router
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
app.include_router(book_router.router)

@app.get("/")
async def root():
    logger.info("Accessed root endpoint")
    return {"message": "Welcome to Book Library Management API"}


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