#!/bin/bash
# test_render_deployment.sh

# Replace this with your actual Render URL once deployed
RENDER_URL="https://your-render-url.onrender.com"

echo "🧪 Testing Render Deployment..."
echo "📍 URL: $RENDER_URL"

echo ""
echo "1️⃣ Testing root endpoint..."
curl -s "$RENDER_URL/" | jq .

echo ""
echo "2️⃣ Testing health endpoint..."
curl -s "$RENDER_URL/health" | jq .

echo ""
echo "3️⃣ Testing user registration..."
curl -s -X POST "$RENDER_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@render.com",
    "password": "TestPass123!",
    "username": "rendertest",
    "role": "Admin"
  }' | jq .

echo ""
echo "4️⃣ Testing login..."
curl -s -X POST "$RENDER_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@render.com",
    "password": "TestPass123!"
  }' | jq .

echo ""
echo "✅ Deployment test completed!"
