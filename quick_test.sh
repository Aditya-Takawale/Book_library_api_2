#!/bin/bash
# Quick test script for Render deployment
# Usage: ./quick_test.sh https://your-render-url.onrender.com

if [ $# -eq 0 ]; then
    echo "Usage: ./quick_test.sh https://your-render-url.onrender.com"
    exit 1
fi

URL=$1

echo "🧪 Testing Render deployment at: $URL"
echo ""

echo "1️⃣ Health check..."
curl -s "$URL/health"
echo ""
echo ""

echo "2️⃣ Root endpoint..."
curl -s "$URL/"
echo ""
echo ""

echo "✅ Basic tests completed!"
