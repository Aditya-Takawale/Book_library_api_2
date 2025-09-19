#!/usr/bin/env python3
"""
Create test users for the Book Library API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.models import *  # Import all models to resolve relationships
from app.utils.auth import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_users():
    """Create test users for different roles"""
    db = SessionLocal()
    
    try:
        # Test users data
        test_users = [
            {
                "email": "aditya@test.com",
                "password": "Aditya@2004",
                "username": "admin_user",
                "first_name": "Aditya",
                "last_name": "Admin",
                "role": UserRole.ADMIN
            },
            {
                "email": "librarian@test.com", 
                "password": "LibPassword123!",
                "username": "librarian_user",
                "first_name": "Library",
                "last_name": "Staff",
                "role": UserRole.LIBRARIAN
            },
            {
                "email": "member@test.com",
                "password": "MemberPass123!",
                "username": "member_user", 
                "first_name": "Regular",
                "last_name": "Member",
                "role": UserRole.MEMBER
            },
            {
                "email": "guest@test.com",
                "password": "GuestPass123!",
                "username": "guest_user",
                "first_name": "Guest",
                "last_name": "User", 
                "role": UserRole.GUEST
            }
        ]
        
        created_users = []
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                logger.info(f"✅ User {user_data['email']} already exists (Role: {existing_user.role.value})")
                continue
            
            # Create new user
            hashed_password = hash_password(user_data["password"])
            
            new_user = User(
                email=user_data["email"],
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                hashed_password=hashed_password,
                role=user_data["role"],
                status=UserStatus.ACTIVE,
                is_active=True,
                email_verified=True,
                failed_login_attempts=0
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            created_users.append({
                "id": new_user.id,
                "email": new_user.email,
                "role": new_user.role.value,
                "password": user_data["password"]  # For display only
            })
            
            logger.info(f"✅ Created user: {new_user.email} (Role: {new_user.role.value})")
        
        # Display all test users
        logger.info("\n" + "="*50)
        logger.info("📋 TEST USER CREDENTIALS")
        logger.info("="*50)
        
        all_test_users = [
            {"email": "aditya@test.com", "password": "Aditya@2004", "role": "ADMIN"},
            {"email": "librarian@test.com", "password": "LibPassword123!", "role": "LIBRARIAN"},
            {"email": "member@test.com", "password": "MemberPass123!", "role": "MEMBER"},
            {"email": "guest@test.com", "password": "GuestPass123!", "role": "GUEST"}
        ]
        
        for user in all_test_users:
            logger.info(f"🔴 {user['role']} User:")
            logger.info(f"   Email: {user['email']}")
            logger.info(f"   Password: {user['password']}")
            logger.info("")
        
        logger.info("="*50)
        logger.info("🎯 You can now log in with any of these credentials!")
        logger.info("🌐 Frontend: http://localhost:3000")
        logger.info("🔐 Secure Test: http://localhost:8000/secure/login-test")
        logger.info("="*50)
        
        return created_users
        
    except Exception as e:
        logger.error(f"❌ Error creating test users: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
