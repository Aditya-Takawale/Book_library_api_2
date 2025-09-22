#!/bin/bash
# test_local_api.sh - Test script for local API development

echo "🧪 Testing Local API..."

API_URL="http://localhost:8000"

echo "1️⃣ Testing health endpoint..."
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

echo "2️⃣ Testing root endpoint..."
curl -s "$API_URL/" | python3 -m json.tool
echo ""

echo "3️⃣ Testing book list endpoint..."
curl -s "$API_URL/books/" | python3 -m json.tool
echo ""

echo "4️⃣ Testing user registration..."
curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@local.com",
    "password": "TestPass123!",
    "username": "localtest",
    "role": "Admin"
  }' | python3 -m json.tool
echo ""

echo "✅ Local API test completed!"
echo "💡 Make sure to start the API server first:"
echo "   cd backend && uvicorn app.main:app --reload --port 8000"
