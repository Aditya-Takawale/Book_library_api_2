from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings
import logging
import secrets

logger = logging.getLogger("BookLibraryAPI")

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Active sessions storage (in production, use Redis or database)
active_sessions: Dict[str, Dict[str, Any]] = {}

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_session_id() -> str:
    """Generate a unique session ID"""
    return secrets.token_urlsafe(32)

def create_tokens(user_data: dict) -> dict:
    """Create both access and refresh tokens with session management"""
    session_id = create_session_id()
    
    token_data = {
        "sub": user_data["email"],
        "role": user_data["role"],
        "session_id": session_id
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store session info
    active_sessions[session_id] = {
        "user_email": user_data["email"],
        "user_role": user_data["role"],
        "created_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow(),
        "is_active": True
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "session_id": session_id
    }

def verify_token(token: str, token_type: str = "access"):
    """Verify and decode a JWT token with session validation"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        session_id: str = payload.get("session_id")
        token_type_claim: str = payload.get("type")
        
        if email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token type
        if token_type_claim != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify session is still active
        if session_id and session_id in active_sessions:
            session = active_sessions[session_id]
            if not session["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session has been terminated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Update last accessed time
            session["last_accessed"] = datetime.utcnow()
        elif session_id:  # Session ID exists but not in active sessions
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "email": email,
            "role": role,
            "session_id": session_id
        }
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def refresh_access_token(refresh_token: str) -> dict:
    """Generate new access token using refresh token"""
    try:
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")
        
        # Create new access token
        token_data = {
            "sub": payload["email"],
            "role": payload["role"],
            "session_id": payload["session_id"]
        }
        
        new_access_token = create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def invalidate_session(session_id: str) -> bool:
    """Invalidate a specific session"""
    if session_id in active_sessions:
        active_sessions[session_id]["is_active"] = False
        logger.info(f"Session {session_id} invalidated")
        return True
    return False

def invalidate_all_user_sessions(user_email: str) -> int:
    """Invalidate all sessions for a specific user"""
    count = 0
    for session_id, session_data in active_sessions.items():
        if session_data["user_email"] == user_email and session_data["is_active"]:
            session_data["is_active"] = False
            count += 1
    logger.info(f"Invalidated {count} sessions for user {user_email}")
    return count

def get_active_sessions(user_email: str = None) -> list:
    """Get active sessions, optionally filtered by user"""
    sessions = []
    for session_id, session_data in active_sessions.items():
        if session_data["is_active"]:
            if user_email is None or session_data["user_email"] == user_email:
                sessions.append({
                    "session_id": session_id,
                    "user_email": session_data["user_email"],
                    "created_at": session_data["created_at"],
                    "last_accessed": session_data["last_accessed"]
                })
    return sessions

def cleanup_expired_sessions():
    """Remove expired and inactive sessions"""
    current_time = datetime.utcnow()
    expired_sessions = []
    
    for session_id, session_data in active_sessions.items():
        # Remove sessions inactive for more than refresh token expiry
        if (current_time - session_data["last_accessed"]).days > REFRESH_TOKEN_EXPIRE_DAYS:
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del active_sessions[session_id]
    
    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    return len(expired_sessions)

def validate_password_strength(password: str) -> bool:
    """Validate password meets strength requirements"""
    import re
    
    # Check minimum length
    if len(password) < 8:
        return False
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for digit
    if not re.search(r'\d', password):
        return False
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def get_password_strength_requirements() -> dict:
    """Return password strength requirements for client-side validation"""
    return {
        "min_length": 8,
        "requires_uppercase": True,
        "requires_lowercase": True,
        "requires_digit": True,
        "requires_special_char": True,
        "special_chars": "!@#$%^&*(),.?\":{}|<>",
        "description": "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character."
    }
