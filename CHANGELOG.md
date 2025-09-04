# Changelog

All notable changes to the Book Library API v2 will be documented in this file.

## [2.0.0] - 2025-09-04

### �� Major Release - Enhanced Edition

#### ✨ Added
- **Role-Based Access Control (RBAC)**
  - 4 user roles: ADMIN, LIBRARIAN, MEMBER, GUEST
  - Granular permission system with 8 different permissions
  - Role-based API endpoint protection
  - User status management (ACTIVE, SUSPENDED, PENDING, DELETED)

- **Enhanced Data Relationships**
  - 14 foreign key relationships across all models
  - Proper CASCADE and SET NULL operations
  - Referential integrity enforcement
  - Bidirectional SQLAlchemy relationships
  - Performance-optimized indexes

- **Loan Management System**
  - Complete loan lifecycle tracking
  - Loan status management (ACTIVE, RETURNED, OVERDUE, RENEWED)
  - Automatic overdue detection and fine calculation
  - Loan renewal system with limits (max 2 renewals)
  - Real-time availability tracking

- **Reservation System**
  - Priority-based reservation queues
  - Automatic expiration handling
  - Queue position tracking
  - Reservation status management (PENDING, FULFILLED, EXPIRED, CANCELLED)

- **Enhanced User Management**
  - JWT authentication with secure token handling
  - Failed login attempt tracking with auto-suspension
  - Last login timestamp tracking
  - User profile management
  - Administrative user operations (suspend, promote, delete)

- **Database Migration System**
  - Alembic-based migrations with CLI tools
  - API endpoints for migration management (`/admin/migration/*`)
  - Database backup and restore functionality
  - Migration history tracking
  - Zero-downtime deployment support

- **Security Enhancements**
  - Comprehensive audit logging for all operations
  - Access attempt tracking with user, resource, and action details
  - Input validation with Pydantic schemas
  - SQL injection protection through ORM
  - Resource ownership enforcement

- **Enhanced Book Management**
  - Multi-author support with role tracking
  - Book popularity metrics (views, downloads, popularity score)
  - Administrative tracking (created_by, updated_by)
  - Advanced search and filtering capabilities
  - Cover image upload and management

- **Review System Enhancements**
  - Review voting system (helpful/not helpful)
  - Helpfulness ratio calculation
  - Spoiler warnings
  - Verified purchase indicators
  - Review moderation capabilities

#### 🏗️ Architecture Improvements
- **Enhanced Models**
  - User model with RBAC fields and methods
  - Book model with popularity tracking and relationships
  - Author model with proper constraints and relationships
  - New BookLoan and BookReservation models
  - Enhanced Review and ReviewVote models

- **API Enhancements**
  - RESTful design with proper HTTP status codes
  - Comprehensive error handling and validation
  - Automatic OpenAPI documentation generation
  - Request/response logging and monitoring

- **Database Optimizations**
  - Proper indexing for performance
  - Unique constraints for business rules
  - Check constraints for data validation
  - Optimized query patterns

#### 📚 Documentation
- Comprehensive README with quick start guide
- RBAC implementation documentation
- Enhanced data relationships documentation
- Migration system documentation
- Setup guide with troubleshooting
- API endpoint documentation

#### 🔐 Security
- JWT token-based authentication
- Role-based authorization
- Permission-based access control
- Audit trail for all operations
- Failed login protection
- Input sanitization and validation

#### 🛠️ Developer Experience
- Structured logging with rotation
- Environment-based configuration
- Docker support
- Development tools integration
- Comprehensive error messages
- Migration CLI tools

### 🔧 Technical Details

#### Database Schema Changes
- Added user roles and status enums
- Created loan and reservation tables
- Enhanced book-author relationship table
- Added audit fields to all models
- Implemented proper foreign key constraints

#### API Endpoints Added
- `/users/*` - User management endpoints
- `/loans/*` - Loan management endpoints
- `/loans/reservations/*` - Reservation management endpoints
- `/admin/migration/*` - Migration management endpoints

#### Dependencies
- No breaking changes to existing dependencies
- Enhanced SQLAlchemy usage with proper relationships
- Alembic for database migrations
- Pydantic for enhanced validation

### 📊 Statistics
- **77 files changed**
- **9,763 insertions**
- **14 foreign key relationships implemented**
- **30+ new API endpoints**
- **4 user roles with granular permissions**
- **Complete loan and reservation system**

---

## [1.0.0] - Previous Version

### Basic Features
- Basic book management
- Simple user authentication
- Basic review system
- SQLAlchemy models
- FastAPI framework

---

**Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
