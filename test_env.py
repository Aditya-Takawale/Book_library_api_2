#!/usr/bin/env python3
"""
Test script to verify environment variables on Railway
"""
import os

print("=== Environment Variables Test ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY', 'NOT SET')}")
print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
print(f"RAILWAY_PROJECT_ID: {os.getenv('RAILWAY_PROJECT_ID', 'NOT SET')}")
print("=" * 40)

# Test database URL parsing
database_url = os.getenv('DATABASE_URL')
if database_url:
    print(f"Database URL found: {database_url[:20]}...")
    if 'yamanote.proxy.rlwy.net' in database_url:
        print("✅ Railway database URL detected")
    else:
        print("❌ Not using Railway database URL")
else:
    print("❌ DATABASE_URL not set")
