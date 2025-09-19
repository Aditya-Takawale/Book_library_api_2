#!/usr/bin/env python3
"""
Simple script to test authentication workflow
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Test login and return token"""
    print("🔐 Testing login...")
    
    login_data = {
        "email": "aditya@test.com",
        "password": "Aditya@2004"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if 'access_token' in data:
            return data['access_token']
        else:
            print("❌ No access_token in response!")
            return None
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    if not token:
        print("❌ No token provided")
        return
    
    print(f"\n🔒 Testing protected endpoint with token...")
    print(f"Token (first 50 chars): {token[:50]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test creating a book
    book_data = {
        "title": "Test Book",
        "genre": "Fiction",
        "page_count": 200,
        "publication_year": 2024,
        "author_ids": [1]  # Assuming author with ID 1 exists
    }
    
    response = requests.post(f"{BASE_URL}/v2/books/", json=book_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Book created successfully!")
    else:
        print(f"❌ Book creation failed")

def main():
    print("🚀 Starting authentication test...\n")
    
    # Test login
    token = test_login()
    
    # Test protected endpoint
    test_protected_endpoint(token)

if __name__ == "__main__":
    main()
