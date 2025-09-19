# Book Library API v2 - Enhanced Edition

🚀 **Advanced Book Library Management System with Enterprise-Grade Features**

## ✨ **What's New in v2**

This is the enhanced version of the Book Library API featuring:
- **Role-Based Access Control ## 🚦 **API Status**

🟢 **Server Running**: Production-ready FastAPI server  
🟢 **Database**: MySQL with all migrations applied  
🟢 **RBAC**: Fully implemented and operational  
🟢 **Loan System**: Complete loan and reservation management  
🟢 **Audit Logging**: Comprehensive access logging  
🟢 **Migration System**: CLI and API migration tools  
🟢 **🔐 Client-Side Encryption**: AES-GCM password encryption system with 4 user roles
- **Enhanced Data Relationships** with proper foreign keys and cascade operations
- **Loan Management System** for library operations
- **Reservation System** with priority queues
- **Comprehensive Audit Logging** for security and compliance
- **Database Migration System** with CLI tools and API endpoints
- **🔐 Client-Side Password Encryption** for enhanced browser security

## 🏗️ **Architecture Overview**

- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: MySQL with Alembic migrations
- **Authentication**: JWT tokens with role-based permissions
- **Security**: RBAC, audit logging, failed login protection
- **API Design**: RESTful with automatic OpenAPI documentation

## 📁 **Project Structure**

```
Book_library_api_2/
├── backend/                      # Backend API server
│   ├── app/                      # FastAPI application
│   │   ├── core/                 # Core functionality
│   │   ├── models/               # SQLAlchemy models
│   │   ├── routers/              # API route handlers
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── utils/                # Utility functions
│   ├── alembic/                  # Database migrations
│   ├── requirements.txt          # Python dependencies
│   ├── venv311/                  # Virtual environment
│   └── logs/                     # Application logs
├── frontend/                     # React TypeScript frontend
│   ├── src/                      # React source code
│   │   ├── components/           # Reusable components
│   │   ├── pages/                # Page components
│   │   ├── services/             # API services
│   │   ├── contexts/             # React contexts
│   │   └── utils/                # Utility functions
│   ├── public/                   # Static assets
│   └── package.json              # Node.js dependencies
├── postman/                      # API testing collections
├── scripts/                      # Deployment scripts
└── docs/                         # Documentation files
```

## 👥 **User Roles & Permissions**

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full system access, user management, all operations |
| **LIBRARIAN** | Book/author management, loan processing, admin panel |
| **MEMBER** | Borrow books, create reviews, manage reservations |
| **GUEST** | Limited read-only access |

## 🔗 **Enhanced Data Relationships**

- **14 Foreign Key Relationships** with proper CASCADE operations
- **Referential Integrity** enforced at database level
- **Audit Trail** tracking who created/modified records
- **Bidirectional SQLAlchemy Relationships** for efficient querying

## 📚 **Core Features**

### 📖 **Book Management**
- CRUD operations with RBAC protection
- Multi-author support with role tracking
- Popularity metrics and view counting
- Cover image upload and management
- Advanced search and filtering

### 👤 **User Management**
- Secure registration with password validation
- Role-based access control
- Account status management (active/suspended/deleted)
- Failed login attempt tracking
- Profile management

### 📝 **Review System**
- User reviews with 1-5 star ratings
- Review voting system (helpful/not helpful)
- Spoiler warnings and verified purchase indicators
- Review moderation and management

### 📋 **Loan Management**
- Complete loan lifecycle tracking
- Automatic overdue detection and fine calculation
- Loan renewal system with limits
- Real-time availability tracking

### 🎫 **Reservation System**
- Priority-based reservation queues
- Automatic expiration handling
- Queue position tracking
- Notification system integration ready

### 🗄️ **Database Migration System**
- Alembic-based migrations with CLI tools
- API endpoints for migration management
- Backup and restore functionality
- Migration history tracking

### 🔐 **Client-Side Password Encryption**
- **AES-GCM Encryption**: Strong 256-bit encryption using Web Crypto API
- **PBKDF2 Key Derivation**: 100,000 iterations with SHA-256 for key generation
- **Perfect Forward Secrecy**: Unique nonce for each encryption session
- **Browser Network Tab Protection**: Passwords never appear in plain text in developer tools
- **Backward Compatibility**: Supports both encrypted and regular login formats
- **Interactive Test Interface**: Real-time encryption testing at `/secure/login-test`

## 🚀 **Quick Start**

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Node.js 18+ (for frontend)

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/Aditya-Takawale/Book_library_api_2.git
cd Book_library_api_2/backend
```

2. **Set up virtual environment**
```bash
python -m venv venv311
source venv311/bin/activate  # On Windows: venv311\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp ../.env.example ../.env
# Edit .env with your database credentials
```

5. **Initialize database**
```bash
alembic upgrade head
```

6. **Start the backend server**
```bash
# For development with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# For production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the frontend development server**
```bash
npm start
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **🔐 Secure Login Test**: http://localhost:8000/secure/login-test

### Quick Development Start

For convenience, you can start both backend and frontend servers with one command:

```bash
# From the project root directory
./start-dev.sh
```

This script will:
- Start the backend API server on port 8000
- Start the frontend React app on port 3000
- Install frontend dependencies if needed
- Display all access points
- Stop both servers when you press Ctrl+C

## 📋 **API Endpoints**

### Authentication & User Management
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (supports both regular and encrypted passwords)
- `GET /users/me` - Get current user profile
- `GET /users/` - List users (admin only)
- `PUT /users/{user_id}` - Update user (admin only)
- `POST /users/{user_id}/suspend` - Suspend user (admin only)

### 🔐 Security & Testing
- `GET /secure/login-test` - Interactive secure login test page with encryption
- `GET /auth/verify` - Verify JWT token and authorization status
- `GET /test/auth` - Interactive token validation interface

### Book Management
- `GET /books/` - List books (public)
- `POST /books/` - Create book (librarian+ only)
- `PUT /books/{book_id}` - Update book (librarian+ only)
- `DELETE /books/{book_id}` - Delete book (admin only)

### Loan Management
- `POST /loans/` - Create loan (librarian+ only)
- `PUT /loans/{loan_id}/return` - Process return (librarian+ only)
- `PUT /loans/{loan_id}/renew` - Renew loan (member+ own loans)
- `GET /loans/user/{user_id}` - Get user loans
- `GET /loans/overdue` - Get overdue loans (librarian+ only)

### Reservation Management
- `POST /loans/reservations` - Create reservation (member+ only)
- `DELETE /loans/reservations/{reservation_id}` - Cancel reservation
- `GET /loans/books/{book_id}/availability` - Check availability

### Migration Management
- `GET /admin/migration/status` - Migration status (admin only)
- `POST /admin/migration/backup` - Create backup (admin only)
- `POST /admin/migration/migrate` - Run migrations (admin only)

## 🛡️ **Security Features**

- **JWT Authentication** with secure token handling
- **🔐 Client-Side Password Encryption** with AES-GCM encryption
- **Role-Based Access Control** with granular permissions
- **Failed Login Protection** with account suspension
- **Audit Logging** for all access attempts
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** through SQLAlchemy ORM
- **Browser Network Tab Protection** - passwords never visible in plain text

## 📊 **Database Schema**

The system includes the following tables with proper relationships:
- `users` - User accounts with RBAC
- `books` - Book catalog with metadata
- `authors` - Author information
- `book_authors` - Many-to-many book-author relationships
- `book_reviews` - User reviews and ratings
- `review_votes` - Review voting system
- `book_loans` - Loan tracking
- `book_reservations` - Reservation queue
- `request_logs` - API request logging

## 🔧 **Development**

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Testing
```bash
# Run tests (when test suite is available)
pytest tests/

# Check API health
curl http://localhost:8000/health

# Test secure login with encryption
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "aditya@test.com", "password": "Aditya@2004"}'

# Access secure login test interface
open http://localhost:8000/secure/login-test
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 📚 **Documentation**

- [RBAC Implementation](RBAC_IMPLEMENTATION.md) - Detailed RBAC system documentation
- [Enhanced Data Relationships](ENHANCED_DATA_RELATIONSHIPS.md) - Database relationship documentation
- [Migration System](MIGRATION_SYSTEM.md) - Database migration documentation

## 🚦 **API Status**

🟢 **Server Running**: Production-ready FastAPI server
🟢 **Database**: MySQL with all migrations applied
🟢 **RBAC**: Fully implemented and operational
�� **Loan System**: Complete loan and reservation management
🟢 **Audit Logging**: Comprehensive access logging
🟢 **Migration System**: CLI and API migration tools

## 🔄 **Version History**

- **v2.1.0** - Added client-side password encryption with AES-GCM, enhanced security features
- **v2.0.0** - Enhanced edition with RBAC, loan management, and advanced features
- **v1.0.0** - Basic book library API

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ **Built With**

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [PyCryptodome](https://pycryptodome.readthedocs.io/) - Cryptographic library for server-side encryption
- [JWT](https://jwt.io/) - JSON Web Tokens for authentication
- [MySQL](https://www.mysql.com/) - Relational database

## 🙏 **Acknowledgments**

- Enhanced with enterprise-grade features for production use
- RBAC system designed for scalability and security
- Database relationships optimized for performance
- Migration system built for zero-downtime deployments

---

**🚀 Ready for production use with enterprise-grade features and client-side encryption security!**

### 🔐 **Test the Secure Login System**

Visit http://localhost:8000/secure/login-test to experience the client-side password encryption in action. You'll see how passwords are encrypted before transmission, keeping them secure from browser network tab inspection.
