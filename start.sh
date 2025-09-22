#!/usr/bin/env bash
# start.sh

set -o errexit  # exit on error

echo "🚀 Starting Book Library API on Render..."

# Change to backend directory
cd backend

# Start the FastAPI application
echo "🌟 Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
