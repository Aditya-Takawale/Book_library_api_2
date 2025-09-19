# Book Library API - Backend

This is the backend server for the Book Library Management System, built with FastAPI.

## Structure

```
backend/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration settings
│   ├── database.py               # Database connection
│   ├── core/                     # Core functionality
│   ├── models/                   # SQLAlchemy models
│   ├── routers/                  # API route handlers
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   └── utils/                    # Utility functions
├── alembic/                      # Database migrations
├── alembic.ini                   # Alembic configuration
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── logs/                         # Application logs
├── static/                       # Static files
├── venv311/                      # Virtual environment
└── test_*.py                     # Test scripts
```

## Quick Start

1. **Setup Virtual Environment**:
   ```bash
   cd backend
   source venv311/bin/activate  # On Windows: venv311\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start the Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Environment Variables

Create a `.env` file in the project root with:

```env
# Database
DATABASE_URL=mysql+pymysql://username:password@localhost/book_library

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_DIR=static/uploads
MAX_FILE_SIZE=5242880  # 5MB
```

## API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing

Run the test scripts:

```bash
python test_auth.py
python test_token.py
```

## Docker

Build and run with Docker:

```bash
docker build -t book-library-api .
docker run -p 8000:8000 book-library-api
```
