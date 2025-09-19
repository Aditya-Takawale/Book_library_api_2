# 📚 Book Library Management API

A comprehensive, production-ready RESTful API for library management built with FastAPI, featuring advanced authentication, role-based access control, and complete CRUD operations.

## 🚀 Features

### 🔐 Authentication & Security
- **JWT-based authentication** with access and refresh tokens
- **Role-Based Access Control (RBAC)** with 4 user roles
- **bcrypt password hashing** with strength validation
- **Session management** and login attempt tracking
- **Email verification system** (admin bypass available)

### 👥 User Management
- **4 User Roles**: Admin, Librarian, Member, Guest
- **4 User Statuses**: Active, Suspended, Pending, Deleted
- **Hierarchical permissions** system
- **User profile management**
- **Admin user management** capabilities

### 📖 Library Operations
- **Complete book CRUD** operations
- **Author management** with relationships
- **Book loan system** with due date tracking
- **Book reservation** functionality
- **Return management** with late fee calculations
- **Book popularity tracking** and analytics

### ⭐ Review System
- **User reviews** with rating system
- **Review voting** (helpful/not helpful)
- **Review moderation** capabilities
- **User review history** tracking

### 🔍 Advanced Features
- **Pagination** support for large datasets
- **Search and filtering** capabilities
- **Database migrations** with Alembic
- **Comprehensive logging** system
- **API documentation** with Swagger UI

## 🏗️ Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: MySQL with SQLAlchemy 2.0 ORM
- **Authentication**: JWT with HTTPBearer
- **Migration**: Alembic
- **Security**: bcrypt password hashing
- **Documentation**: OpenAPI/Swagger UI
- **Environment**: Virtual environment (venv311)

## 📁 Project Structure

```
Book_library_api_2/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   │
│   ├── models/                 # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py            # User model with roles & relationships
│   │   ├── book.py            # Book model with author relationships
│   │   ├── loan.py            # BookLoan & BookReservation models
│   │   ├── review.py          # Review & ReviewVote models
│   │   ├── author.py          # Author model
│   │   └── request_log.py     # Request logging model
│   │
│   ├── schemas/               # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py           # User request/response models
│   │   ├── book.py           # Book validation schemas
│   │   ├── loan.py           # Loan validation schemas
│   │   ├── review.py         # Review validation schemas
│   │   └── author.py         # Author validation schemas
│   │
│   ├── routers/              # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── book.py           # Book CRUD operations
│   │   ├── book_enhanced.py  # Enhanced book operations
│   │   ├── user_management.py # User management
│   │   ├── loan.py           # Loan operations
│   │   ├── review.py         # Review system
│   │   ├── author.py         # Author management
│   │   └── migration.py      # Migration endpoints
│   │
│   ├── services/             # Business logic layer
│   │   ├── user_service.py   # User business logic
│   │   ├── book_service.py   # Book business logic
│   │   ├── loan_service.py   # Loan business logic
│   │   ├── review_service.py # Review business logic
│   │   └── author_service.py # Author business logic
│   │
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT token management
│   │   ├── rbac.py          # Role-based access control
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   ├── logger.py        # Logging configuration
│   │   ├── migrations.py    # Migration utilities
│   │   └── migration_config.py # Migration configuration
│   │
│   └── core/                # Core modules
│       └── db.py           # Database core functionality
│
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/           # Migration versions
│
├── logs/                   # Application logs
├── postman/               # Postman collections
├── scripts/               # Deployment scripts
├── venv311/              # Virtual environment
├── requirements.txt      # Python dependencies
├── alembic.ini          # Alembic configuration
└── Dockerfile           # Docker configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MySQL database
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Book_library_api_2
```

2. **Create and activate virtual environment**
```bash
python -m venv venv311
source venv311/bin/activate  # On Windows: venv311\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
- Update database connection in `app/config.py`
- Ensure MySQL server is running

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the application**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

7. **Access the API**
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## 🔑 User Roles & Permissions

### Role Hierarchy (Highest to Lowest)

#### 1. **ADMIN** 👑
- **Full system access**
- User management (create, update, delete users)
- All book and author operations
- Loan management for all users
- System configuration access
- **Bypasses email verification requirement**

#### 2. **LIBRARIAN** 📚
- Book and author management
- Loan processing and management
- Review moderation
- Access to admin panel features
- Cannot manage other users

#### 3. **MEMBER** 👤
- Create and manage personal account
- Borrow and return books
- Create and manage reviews
- View book catalog and search
- Basic user functionality

#### 4. **GUEST** 👻
- Limited read-only access
- Browse book catalog
- View public information
- Cannot borrow books or create reviews

### User Status Types
- **ACTIVE**: Normal functioning account
- **SUSPENDED**: Temporarily disabled
- **PENDING**: Awaiting activation/verification
- **DELETED**: Marked for deletion

## 🔐 Authentication

### Registration
```bash
POST /auth/register
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "Member"
}
```

### Login
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePassword123!
```

### Using JWT Token
```bash
Authorization: Bearer <your_jwt_token>
```

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - User logout

### User Management (Admin/Librarian)
- `GET /users/` - List all users
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /users/me` - Get current user profile

### Books
- `GET /books/` - List books (with pagination)
- `POST /books/` - Create new book (Librarian+)
- `GET /books/{book_id}` - Get book details
- `PUT /books/{book_id}` - Update book (Librarian+)
- `DELETE /books/{book_id}` - Delete book (Librarian+)
- `GET /books/search` - Search books

### Authors
- `GET /authors/` - List authors
- `POST /authors/` - Create author (Librarian+)
- `GET /authors/{author_id}` - Get author details
- `PUT /authors/{author_id}` - Update author (Librarian+)
- `DELETE /authors/{author_id}` - Delete author (Librarian+)

### Loans
- `GET /loans/` - List loans
- `POST /loans/` - Create loan (Librarian+)
- `GET /loans/{loan_id}` - Get loan details
- `PUT /loans/{loan_id}/return` - Return book
- `GET /loans/user/{user_id}` - Get user's loans

### Reviews
- `GET /reviews/` - List reviews
- `POST /reviews/` - Create review (Member+)
- `GET /reviews/{review_id}` - Get review details
- `PUT /reviews/{review_id}` - Update review
- `DELETE /reviews/{review_id}` - Delete review
- `POST /reviews/{review_id}/vote` - Vote on review

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=mysql://username:password@localhost/book_library

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### Database Configuration
Update `app/config.py` with your database settings:

```python
DATABASE_URL = "mysql://username:password@localhost/book_library"
SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

## 🧪 Testing

### Using Swagger UI
1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Login to get JWT token
4. Enter token in format: `Bearer <your_token>`
5. Test any endpoint

### Using curl
```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "role": "Member"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123!"

# Access protected endpoint
curl -X GET "http://localhost:8000/books/" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### Sample Test Data

#### Create Admin User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@library.com",
    "username": "admin",
    "password": "AdminPassword123!",
    "first_name": "Library",
    "last_name": "Administrator",
    "role": "Admin"
  }'
```

#### Create Test Book
```bash
curl -X POST "http://localhost:8000/books/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "isbn": "9780743273565",
    "publication_year": 1925,
    "genre": "Fiction",
    "description": "A classic American novel",
    "total_copies": 5,
    "available_copies": 5
  }'
```

## 📊 Database Schema

### Key Relationships
- **Users** ↔ **BookLoans** (borrower relationship)
- **Users** ↔ **BookReviews** (review author)
- **Books** ↔ **Authors** (many-to-many)
- **Books** ↔ **BookLoans** (loan history)
- **Books** ↔ **BookReviews** (review target)

### Indexes for Performance
- User email and status
- User role and status
- Book title and genre
- Loan dates and status

## 🚀 Deployment

### Using Docker
```bash
# Build image
docker build -t book-library-api .

# Run container
docker run -p 8000:8000 book-library-api
```

### Production Considerations
- Use environment variables for sensitive data
- Configure proper logging levels
- Set up database connection pooling
- Enable CORS for frontend integration
- Use reverse proxy (nginx) for production
- Set up SSL/TLS certificates

## 📝 Migration System

### Create New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one revision
alembic downgrade -1
```

### Migration History
```bash
alembic history
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Errors
- **Issue**: "JWT verification failed: Not enough segments"
- **Solution**: Ensure token format is `Bearer <token>` in Swagger UI

#### 2. Database Connection
- **Issue**: Cannot connect to MySQL
- **Solution**: Check database URL and ensure MySQL service is running

#### 3. Permission Denied
- **Issue**: 403 Forbidden on admin endpoints
- **Solution**: Ensure user has correct role and email verification status

#### 4. Email Verification Required
- **Issue**: "Email verification required to access this resource"
- **Solution**: Admin users bypass this requirement automatically

### Logs Location
- Application logs: `logs/app_YYYYMMDD.log`
- Check logs for detailed error information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM capabilities
- Pydantic for data validation
- Alembic for database migrations

## 📞 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the troubleshooting section
- Check application logs for errors

---

**Built with ❤️ using FastAPI and Python**
