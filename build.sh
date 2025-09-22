#!/usr/bin/env bash
# build.sh

set -o errexit  # exit on error

echo "🔧 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "✅ Build completed successfully!"
