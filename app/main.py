from fastapi import FastAPI
from app.routers import book as book_router
from app.database import engine
from app.models import book as book_model
from app.utils.logger import setup_logger

app = FastAPI(title="Book Library Management API")

# Initialize logger
setup_logger()

# Create database tables
book_model.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(book_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Book Library Management API"}
