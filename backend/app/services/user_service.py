from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserRegistration, UserResponse, UserUpdate
from app.utils.auth import hash_password, verify_password, create_tokens
import logging
from logging.handlers import RotatingFileHandler
import os

# Setup database access logger
access_log_dir = "logs"
os.makedirs(access_log_dir, exist_ok=True)
db_access_logger = logging.getLogger("DBAccessLogger")
db_access_logger.setLevel(logging.INFO)
if not db_access_logger.hasHandlers():
    db_access_logger.addHandler(RotatingFileHandler(
        f"{access_log_dir}/db_access.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    ))

logger = logging.getLogger("BookLibraryAPI")

class UserService:
    
    @staticmethod
    def create_user(db: Session, user_data: UserRegistration) -> User:
        """Create a new user with validation and password hashing"""
        try:
            # Check if email already exists
            existing_user_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_user_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Check if username already exists
            existing_user_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_user_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            
            # Hash the password
            hashed_password = hash_password(user_data.password)
            
            # Create new user with enhanced fields
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role,
                status=UserStatus.ACTIVE,
                is_active=True,
                email_verified=False,  # Can be verified later via email confirmation
                failed_login_attempts=0
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"✅ User created successfully: {db_user.email} (ID: {db_user.id})")
            db_access_logger.info(f"User registration: email={user_data.email}, username={user_data.username}, role={user_data.role}")
            return db_user
            
        except HTTPException:
            # Re-raise HTTPExceptions without modification
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def login_user(db: Session, email: str, password: str) -> dict:
        """Login user and create session with tokens"""
        # Log login attempt (mask password)
        db_access_logger.info(f"Login attempt: email={email}, password=[MASKED]")
        user = UserService.authenticate_user(db, email, password)
        if not user:
            db_access_logger.warning(f"Failed login for email={email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens with session management
        user_data = {
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "user_id": user.id
        }
        
        logger.info(f"Creating tokens for user: {user.email}, role: {user_data['role']}")
        tokens = create_tokens(user_data)
        
        # Add user info to response
        tokens["user"] = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        
        db_access_logger.info(f"Successful login for email={email}, user_id={user.id}, role={user.role}")
        logger.info(f"User {user.email} logged in successfully. Session: {tokens['session_id']}")
        return tokens
            
    @staticmethod
    def update_user_status(db: Session, user_id: int, is_active: bool) -> User:
        """Update user active status"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {user.email} status updated to: {'active' if is_active else 'inactive'}")
        return user
    
    @staticmethod
    def change_user_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password with current password verification"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        return True
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # Update only provided fields
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {user.email} updated: {list(update_data.keys())}")
        return user
    
    @staticmethod
    def get_all_users(
        db: Session, 
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Get all users with filtering and pagination"""
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        if status:
            query = query.filter(User.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_statistics(db: Session) -> Dict[str, Any]:
        """Get user statistics for admin dashboard"""
        total_users = db.query(User).count()
        
        # Count by role
        role_counts = {}
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            role_counts[role.value] = count
        
        # Count by status
        status_counts = {}
        for status in UserStatus:
            count = db.query(User).filter(User.status == status).count()
            status_counts[status.value] = count
        
        # Active users
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # Recent registrations (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_registrations = db.query(User).filter(User.created_at >= thirty_days_ago).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "role_distribution": role_counts,
            "status_distribution": status_counts,
            "recent_registrations": recent_registrations
        }
    
    @staticmethod
    def increment_failed_login(db: Session, email: str) -> None:
        """Increment failed login attempts for security tracking"""
        user = UserService.get_user_by_email(db, email)
        if user:
            user.failed_login_attempts += 1
            
            # Auto-suspend after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.status = UserStatus.SUSPENDED
                logger.warning(f"User {email} suspended due to excessive failed login attempts")
            
            db.commit()
    
    @staticmethod
    def reset_failed_login_attempts(db: Session, user_id: int) -> None:
        """Reset failed login attempts after successful login"""
        user = UserService.get_user_by_id(db, user_id)
        if user:
            user.failed_login_attempts = 0
            db.commit()
