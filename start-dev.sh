#!/bin/bash

# Book Library API v2 - Development Server Starter
# This script starts both the backend API server and frontend React app

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Book Library API v2 - Development Server Starter${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: backend/ and frontend/ directories not found.${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

echo -e "${YELLOW}📋 Starting services...${NC}"
echo ""

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    jobs -p | xargs kill 2>/dev/null || true
    wait
    echo -e "${GREEN}✅ All servers stopped.${NC}"
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend server
echo -e "${BLUE}🔧 Starting Backend API Server...${NC}"
cd backend
if [ ! -d "venv311" ]; then
    echo -e "${RED}❌ Virtual environment not found in backend/venv311${NC}"
    echo "Please set up the backend first. See backend/README.md"
    exit 1
fi

source venv311/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend server starting on http://localhost:8001${NC}"
echo ""

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo -e "${BLUE}🎨 Starting Frontend React App...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

npm start &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Frontend server starting on http://localhost:3000${NC}"
echo ""

echo -e "${GREEN}🎉 Both servers are starting up!${NC}"
echo ""
echo -e "${BLUE}📊 Access Points:${NC}"
echo -e "  • Frontend:     ${GREEN}http://localhost:3000${NC}"
echo -e "  • Backend API:  ${GREEN}http://localhost:8001${NC}"
echo -e "  • API Docs:     ${GREEN}http://localhost:8001/docs${NC}"
echo -e "  • Secure Test:  ${GREEN}http://localhost:8001/secure/login-test${NC}"
echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop both servers${NC}"
echo ""

# Wait for background processes
wait
