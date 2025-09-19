from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Union
from app.database import get_db
from app.schemas.user import UserRegistration, UserResponse, UserLogin, EncryptedUserLogin, PasswordChangeRequest, UserUpdate, TokenResponse
from app.services.user_service import UserService
from app.utils.auth import create_access_token, get_password_strength_requirements, refresh_access_token, invalidate_session, invalidate_all_user_sessions, get_active_sessions, cleanup_expired_sessions
from app.utils.dependencies import get_current_user, get_admin_user, get_current_active_user, require_admin, require_member
from app.utils.rbac import require_admin_user, require_member_user, log_access_attempt
from app.utils.encryption import decrypt_login_data
from app.models.user import UserRole, UserStatus
from datetime import timedelta
import logging

logger = logging.getLogger("BookLibraryAPI")

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Register a new user account with email validation and password strength requirements.
    
    **Password Requirements:**
    - At least 8 characters long
    - At least one uppercase letter
    - At least one lowercase letter  
    - At least one digit
    - At least one special character (!@#$%^&*(),.?":{}|<>)
    
    **Role Options:**
    - Admin: Full access to all operations
    - Member: Limited access (default)
    """
    logger.info(f"📝 New user registration attempt: {user_data.email}")
    
    # Create user through service
    new_user = UserService.create_user(db, user_data)
    
    logger.info(f"✅ User registered successfully: {new_user.email} (Role: {new_user.role.value})")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role.value,
        is_active=new_user.is_active,
        email_verified=new_user.email_verified,
        created_at=new_user.created_at
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: Union[UserLogin, EncryptedUserLogin],
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token with refresh token and session management.
    
    Supports both regular and encrypted password formats for enhanced security.
    
    Returns:
    - access_token: JWT token for API access (expires in 30 minutes)
    - refresh_token: JWT token for refreshing access token (expires in 7 days)
    - session_id: Unique session identifier for session management
    - user: User information
    """
    logger.info(f"🔐 Login attempt for: {login_data.email}")
    
    try:
        # Check if this is encrypted login data
        if hasattr(login_data, 'encrypted') and login_data.encrypted:
            logger.info(f"🔒 Processing encrypted login for: {login_data.email}")
            
            # Decrypt the login data
            encrypted_data = {
                'email': login_data.email,
                'password': login_data.password,
                'nonce': login_data.nonce,
                'tag': login_data.tag,
                'encrypted': True
            }
            
            decrypted_data = decrypt_login_data(encrypted_data)
            email = decrypted_data['email']
            password = decrypted_data['password']
            
            logger.info(f"🔓 Password decrypted successfully for: {email}")
        else:
            # Regular login (backward compatibility)
            logger.info(f"🔑 Processing regular login for: {login_data.email}")
            email = login_data.email
            password = login_data.password
        
        # Use the enhanced login method that creates tokens with session
        tokens_response = UserService.login_user(db, email, password)
        
        logger.info(f"✅ Successful login: {email}")
        return tokens_response
        
    except ValueError as ve:
        logger.error(f"❌ Decryption failed for {login_data.email}: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid encrypted login data"
        )
    except Exception as e:
        logger.error(f"❌ Login failed for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all users (Admin access required).
    """
    try:
        logger.info(f"📋 Admin {current_user.email} fetching users list (skip: {skip}, limit: {limit})")
        
        users = UserService.get_all_users(db, skip=skip, limit=limit)
        
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value,
                is_active=user.is_active,
                email_verified=user.email_verified,
                created_at=user.created_at
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"❌ Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )

@router.get("/password-requirements")
async def get_password_requirements():
    """
    Get password strength requirements for client-side validation.
    """
    return {
        "requirements": get_password_strength_requirements(),
        "examples": {
            "valid": "MyPassword123!",
            "invalid_examples": {
                "too_short": "Pass1!",
                "no_uppercase": "mypassword123!",
                "no_lowercase": "MYPASSWORD123!",
                "no_digit": "MyPassword!",
                "no_special": "MyPassword123"
            }
        }
    }

@router.get("/verify-email/{user_id}")
async def verify_email(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Verify user email (placeholder for email verification flow).
    """
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # In a real implementation, you would verify a token here
        # For now, we'll just mark as verified
        user.email_verified = True
        db.commit()
        
        logger.info(f"✅ Email verified for user: {user.email}")
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/refresh")
async def refresh_token(
    refresh_token_data: dict
):
    """
    Refresh access token using refresh token.
    
    Request body:
    {
        "refresh_token": "your_refresh_token_here"
    }
    """
    try:
        refresh_token = refresh_token_data.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        # Generate new access token
        new_tokens = refresh_access_token(refresh_token)
        
        logger.info("✅ Access token refreshed successfully")
        return new_tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout_user(
    current_user = Depends(get_current_user)
):
    """
    Logout current user and invalidate their session.
    """
    try:
        session_id = getattr(current_user, 'current_session_id', None)
        if session_id:
            invalidated = invalidate_session(session_id)
            if invalidated:
                logger.info(f"✅ User {current_user.email} logged out. Session {session_id} invalidated")
                return {"message": "Logged out successfully"}
        
        return {"message": "No active session found"}
        
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/logout-all")
async def logout_all_sessions(
    current_user = Depends(get_current_user)
):
    """
    Logout user from all devices/sessions.
    """
    try:
        count = invalidate_all_user_sessions(current_user.email)
        logger.info(f"✅ All sessions invalidated for user {current_user.email}. Count: {count}")
        
        return {
            "message": f"Logged out from {count} sessions successfully",
            "sessions_invalidated": count
        }
        
    except Exception as e:
        logger.error(f"❌ Logout all sessions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout from all sessions failed"
        )

@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at,
        "session_id": getattr(current_user, 'current_session_id', None)
    }

@router.get("/sessions")
async def get_user_sessions(
    current_user = Depends(get_current_user)
):
    """
    Get all active sessions for the current user.
    """
    try:
        sessions = get_active_sessions(current_user.email)
        return {
            "active_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"❌ Get sessions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )

@router.delete("/sessions/{session_id}")
async def invalidate_specific_session(
    session_id: str,
    current_user = Depends(get_admin_user)
):
    """
    Invalidate a specific session (Admin only).
    """
    try:
        invalidated = invalidate_session(session_id)
        if invalidated:
            logger.info(f"✅ Session {session_id} invalidated by admin {current_user.email}")
            return {"message": f"Session {session_id} invalidated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session invalidation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session invalidation failed"
        )

@router.post("/cleanup-sessions")
async def cleanup_expired_sessions_endpoint(
    current_user = Depends(get_admin_user)
):
    """
    Cleanup expired sessions (Admin only).
    """
    try:
        cleaned_count = cleanup_expired_sessions()
        logger.info(f"✅ {cleaned_count} expired sessions cleaned up by admin {current_user.email}")
        
        return {
            "message": "Session cleanup completed",
            "sessions_removed": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"❌ Session cleanup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session cleanup failed"
        )
