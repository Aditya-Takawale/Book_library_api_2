from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session
from app.utils.auth import verify_token
from app.services.user_service import UserService
from app.database import get_db
from app.schemas.user import UserResponse, UserRole, UserStatus
import logging
from datetime import datetime

logger = logging.getLogger("BookLibraryAPI")

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Dependency to get current authenticated user
    """
    try:
        logger.debug(f"Received credentials: {credentials.scheme if credentials else 'None'}")
        logger.debug(f"Token received: '{credentials.credentials[:50] if credentials and credentials.credentials else 'None'}...'")
        
        if not credentials:
            logger.warning("No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not credentials.credentials:
            logger.warning("Empty token in credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing in Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token and get user data
        token_data = verify_token(credentials.credentials)
        
        # Get user from database
        user = UserService.get_user_by_email(db, token_data["email"])
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check user status
        if hasattr(user, 'status') and user.status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is suspended",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if hasattr(user, 'status') and user.status == UserStatus.DELETED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account no longer exists",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login
        if hasattr(user, 'last_login'):
            user.last_login = datetime.now()
            user.failed_login_attempts = 0  # Reset on successful auth
            db.commit()
        
        # Add session info to user object
        user.current_session_id = token_data.get("session_id")
        
        # Convert to UserResponse with permissions
        user_response = UserResponse.from_orm(user)
        if hasattr(user, 'get_permissions'):
            user_response.permissions = user.get_permissions()
        
        # Log successful authorization with user details
        logger.info(f"🔐 AUTHORIZATION SUCCESS: User '{user_response.email}' (Role: {user_response.role}) authenticated successfully!")
        logger.debug(f"Authentication successful for user: {user_response.email}")
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency to get current active user (alias for clarity)
    """
    return current_user

async def get_admin_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency to ensure current user is an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_librarian_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency to ensure current user is a librarian or admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Librarian or Admin access required"
        )
    return current_user

async def get_member_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency to ensure current user is at least a member
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.MEMBER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Member access or higher required"
        )
    return current_user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserResponse]:
    """
    Dependency for optional authentication (returns None if no token)
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

class RequireRole:
    """
    Class-based dependency to require specific roles
    """
    def __init__(self, required_roles: list):
        self.required_roles = required_roles
    
    def __call__(self, current_user: UserResponse = Depends(get_current_user)):
        if current_user.role not in self.required_roles:
            role_names = [role.value if hasattr(role, 'value') else str(role) for role in self.required_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(role_names)}"
            )
        return current_user

class RequirePermission:
    """
    Class-based dependency to require specific permissions
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(self, current_user: UserResponse = Depends(get_current_user)):
        if self.required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {self.required_permission}"
            )
        return current_user

# Convenience role dependencies
require_admin = RequireRole([UserRole.ADMIN])
require_librarian = RequireRole([UserRole.ADMIN, UserRole.LIBRARIAN])
require_member = RequireRole([UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.MEMBER])

# Permission dependencies
require_manage_books = RequirePermission("manage_books")
require_manage_authors = RequirePermission("manage_authors")
require_manage_users = RequirePermission("manage_users")
require_admin_panel = RequirePermission("admin_panel")
