#!/bin/bash

# Railway Deployment Preparation Script
# This script prepares your project for Railway deployment

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚆 Railway Deployment Preparation${NC}"
echo ""

# Create railway deployment files
echo -e "${YELLOW}📋 Creating Railway configuration files...${NC}"

# Create Procfile for backend
cat > backend/Procfile << 'EOF'
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
EOF

# Create railway.json for project configuration
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
EOF

# Create requirements.txt if not exists (for Railway auto-detection)
if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${YELLOW}📦 Creating requirements.txt...${NC}"
    cat > backend/requirements.txt << 'EOF'
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.35
pymysql==1.1.1
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
pydantic-settings==2.4.0
alembic==1.13.2
pycryptodome==3.20.0
cryptography==42.0.8
mysql-connector-python==9.0.0
EOF
fi

# Create environment variables template for Railway
cat > .env.railway << 'EOF'
# Railway Environment Variables
# Copy these to your Railway project environment variables

DATABASE_URL=mysql+pymysql://root:password@mysql:3306/railway
SECRET_KEY=your-super-secure-secret-key-here-32-chars-minimum
LOG_LEVEL=INFO
UPLOAD_DIR=uploads

# Frontend URL (will be provided by Railway)
FRONTEND_URL=https://your-frontend-url.railway.app

# CORS Origins (add your Railway URLs)
CORS_ORIGINS=https://your-frontend-url.railway.app,https://your-backend-url.railway.app
EOF

echo -e "${GREEN}✅ Railway configuration files created!${NC}"
echo ""

echo -e "${BLUE}📋 Next Steps for Railway Deployment:${NC}"
echo ""
echo -e "${YELLOW}1. Push to GitHub:${NC}"
echo "   git add ."
echo "   git commit -m 'Add Railway deployment config'"
echo "   git push origin main"
echo ""
echo -e "${YELLOW}2. Deploy on Railway:${NC}"
echo "   • Go to https://railway.app"
echo "   • Sign in with GitHub"
echo "   • Click 'New Project' → 'Deploy from GitHub repo'"
echo "   • Select your Book_library_api_2 repository"
echo "   • Railway will auto-detect FastAPI backend"
echo ""
echo -e "${YELLOW}3. Add Database:${NC}"
echo "   • Click 'Add Service' → 'Database' → 'MySQL'"
echo "   • Copy the connection URL to environment variables"
echo ""
echo -e "${YELLOW}4. Set Environment Variables:${NC}"
echo "   • Go to your backend service settings"
echo "   • Add variables from .env.railway file"
echo "   • Update DATABASE_URL with Railway MySQL URL"
echo ""
echo -e "${YELLOW}5. Deploy Frontend:${NC}"
echo "   • Add another service from same repo"
echo "   • Select 'frontend' folder as root directory"
echo "   • Railway will auto-detect React app"
echo ""
echo -e "${GREEN}🎉 Your app will be live at https://yourapp.railway.app${NC}"
echo ""
echo -e "${BLUE}💡 Pro Tips:${NC}"
echo "   • Railway provides $5 free credits monthly"
echo "   • Auto-deploys on every git push"
echo "   • Built-in database backups"
echo "   • Custom domains available"
echo ""
