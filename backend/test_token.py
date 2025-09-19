#!/usr/bin/env python3
"""
Test script to verify the provided JWT token
"""
import requests
import json
import jwt
import base64
from datetime import datetime, timezone

# Your provided token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGl0eWFAdGVzdC5jb20iLCJyb2xlIjoiQWRtaW4iLCJzZXNzaW9uX2lkIjoiUVhLajBaZThRTUFZMmxrTjBBMTQ5UG5ObXJ3MXRtRXc2WnFLaENqTzFDSSIsImV4cCI6MTc1NzUwMTQxOSwidHlwZSI6ImFjY2VzcyJ9.FAT8-jK4bibNVLHtjOaVlq1-qL0SRqsJNyl75QEdWnA"

def decode_token_without_verification(token):
    """Decode JWT token without signature verification to inspect contents"""
    try:
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            return None, f"Invalid token format: {len(parts)} parts instead of 3"
        
        # Decode header
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
        
        # Decode payload
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
        
        return {"header": header, "payload": payload}, None
    except Exception as e:
        return None, f"Failed to decode token: {str(e)}"

def test_token():
    print("🔍 ANALYZING YOUR TOKEN...")
    print("=" * 60)
    
    # Decode token to inspect contents
    decoded, error = decode_token_without_verification(TOKEN)
    
    if error:
        print(f"❌ Token decode error: {error}")
        return
    
    print("✅ Token structure is valid")
    print(f"📋 Header: {json.dumps(decoded['header'], indent=2)}")
    print(f"📋 Payload: {json.dumps(decoded['payload'], indent=2)}")
    
    # Check expiration
    exp_timestamp = decoded['payload'].get('exp', 0)
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    
    print(f"\n⏰ Token expires: {exp_datetime}")
    print(f"⏰ Current time: {current_time}")
    
    if exp_datetime > current_time:
        time_left = exp_datetime - current_time
        print(f"✅ Token is valid for {time_left}")
    else:
        time_expired = current_time - exp_datetime
        print(f"❌ Token expired {time_expired} ago")
        return
    
    print("\n🧪 TESTING TOKEN WITH API...")
    print("=" * 60)
    
    # Test with the actual API
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test creating a book
    book_data = {
        "title": "Token Test Book",
        "author": "Test Author",
        "isbn": "978-1234567890",
        "published_year": 2023,
        "publication_year": 2023,  # Added required field
        "page_count": 200,  # Added required field
        "genre": "Technology",
        "description": "A test book to verify token works",
        "author_ids": []  # Added required field
    }
    
    try:
        print("📚 Testing book creation...")
        response = requests.post(
            "http://localhost:8000/v2/books/",
            headers=headers,
            json=book_data,
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ SUCCESS! Token works perfectly!")
            result = response.json()
            print(f"📖 Created book: {result}")
        elif response.status_code == 401:
            print("❌ AUTHENTICATION FAILED!")
            print(f"📄 Response: {response.text}")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_token()
