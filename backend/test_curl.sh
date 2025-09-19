#!/bin/bash

echo "🔐 Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aditya@test.com",
    "password": "admin123"
  }')

echo "Login response: $LOGIN_RESPONSE"

# Extract access token using Python
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo -e "\n🎫 Using token: ${ACCESS_TOKEN:0:50}..."

echo -e "\n📚 Testing book creation..."
curl -X POST "http://localhost:8000/v2/books/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Curl Test Book",
    "author": "Test Author",
    "isbn": "978-1234567890",
    "published_year": 2023,
    "genre": "Technology",
    "description": "A test book created via cURL"
  }' | python3 -m json.tool

echo -e "\n✅ Test completed!"
