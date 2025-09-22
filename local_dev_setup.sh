#!/bin/bash
# local_dev_setup.sh - Setup script for local development

echo "🚀 Setting up local development environment..."

# Create local .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating local .env file..."
    cat > backend/.env << EOF
# Local Development Configuration
DATABASE_URL=mysql+pymysql://root:@localhost:3306/library_db
SECRET_KEY=local-dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000
LOG_LEVEL=INFO
EOF
    echo "✅ Local .env file created"
else
    echo "✅ Local .env file already exists"
fi

# Check if MySQL is running
echo "🔍 Checking MySQL connection..."
if command -v mysql &> /dev/null; then
    if mysql -u root -e "SELECT 1;" &> /dev/null; then
        echo "✅ MySQL is running"
        
        # Create database if it doesn't exist
        mysql -u root -e "CREATE DATABASE IF NOT EXISTS library_db;" 2>/dev/null
        echo "✅ Database 'library_db' ready"
    else
        echo "❌ MySQL is not running or connection failed"
        echo "💡 Please start MySQL and ensure root user has access"
    fi
else
    echo "❌ MySQL not found"
    echo "💡 Please install MySQL: brew install mysql (macOS) or sudo apt install mysql-server (Ubuntu)"
fi

echo ""
echo "🏃‍♂️ To start the development server:"
echo "  cd backend"
echo "  pip install -r requirements.txt"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 API will be available at: http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
