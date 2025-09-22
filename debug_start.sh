#!/bin/bash
echo "🔍 Debug: Environment Variables"
echo "PORT: $PORT"
echo "DATABASE_URL exists: $([ -n "$DATABASE_URL" ] && echo "YES" || echo "NO")"
echo "SECRET_KEY exists: $([ -n "$SECRET_KEY" ] && echo "YES" || echo "NO")"
echo ""
echo "🔍 Debug: Python and directory check"
python3 --version
pwd
ls -la
echo ""
echo "🔍 Debug: Backend directory check"
cd backend
pwd
ls -la
echo ""
echo "🚀 Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
