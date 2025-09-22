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

# Fix Railway detection issue
echo -e "${YELLOW}� Fixing Railway monorepo detection...${NC}"

# Update railway.json for monorepo
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
EOF

# Create root-level requirements.txt for Railway detection
cat > requirements.txt << 'EOF'
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.35
pymysql==1.1.0
pydantic-settings==2.2.1
python-dotenv==1.0.1
fastapi-pagination==0.12.25
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
email-validator==2.1.0
alembic==1.16.5
pycryptodome==3.20.0
cryptography==42.0.8
mysql-connector-python==9.0.0
EOF

# Update Procfile
cat > Procfile << 'EOF'
web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
EOF

# Create Python detection file
cat > main.py << 'EOF'
# Railway deployment setup for Book Library API
print("Railway deployment setup for Book Library API")
EOF

# Create runtime specification
echo "python" > runtime.txt

echo -e "${GREEN}✅ Railway configuration files updated!${NC}"
echo ""

echo -e "${RED}⚠️  IMPORTANT: Railway Monorepo Deployment Strategy${NC}"
echo ""
echo -e "${BLUE}📋 Updated Deployment Steps:${NC}"
echo ""
echo -e "${YELLOW}1. Deploy Backend First:${NC}"
echo "   • Go to Railway dashboard"
echo "   • Create 'New Project' from GitHub"
echo "   • Select your repository"
echo "   • Railway will now detect Python correctly"
echo ""
echo -e "${YELLOW}2. Add MySQL Database:${NC}"
echo "   • Click 'New' → 'Database' → 'MySQL'"
echo "   • Copy DATABASE_URL to environment variables"
echo ""
echo -e "${YELLOW}3. Set Environment Variables:${NC}"
echo "   • Go to your service settings → Variables"
echo "   • Add from .env.railway file"
echo ""
echo -e "${YELLOW}4. Deploy Frontend Separately:${NC}"
echo "   • Create another service in same project"
echo "   • Choose 'Deploy from GitHub repo'"
echo "   • Set 'Root Directory' to 'frontend'"
echo "   • Or use Vercel for better frontend performance"
echo ""
echo -e "${GREEN}🎉 Backend will be live at https://yourapp.railway.app${NC}"
echo ""
echo -e "${BLUE}💡 Alternative: Split Deployment${NC}"
echo "   • Backend: Railway (what we just configured)"
echo "   • Frontend: Vercel or Netlify (free, faster)"
echo "   • Database: Railway MySQL (included)"
echo ""
