
# Book Library Management API

A RESTful API for managing a digital book library built with FastAPI and MySQL.

## Features
- CRUD operations for books
- File upload for book cover images
- Pagination support
- Author-based book queries
- Text search functionality
- Multi-criteria filtering
- Comprehensive logging
- Input validation with Pydantic
- Postman collection for API testing

## Prerequisites
- Python 3.11+ or 3.13
- MySQL 8.0 (managed by Homebrew)
- MySQL Workbench
- Docker (optional)
- Homebrew (required)

## Setup Instructions (macOS)

1. **Ensure MySQL is Running**:
   ```bash
   brew services list
   brew services start mysql