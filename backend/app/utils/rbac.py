"""
Role-Based Access Control (RBAC) dependencies and decorators.
"""
from functools import wraps
from typing import List, Optional, Union, Callable, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.utils.dependencies import get_current_user, get_db
from app.models.user import User, UserStatus
from app.schemas.user import UserResponse, UserRole
import logging

logger = logging.getLogger("RBAC")
security = HTTPBearer()

# RBAC Exceptions
class InsufficientPermissionsError(HTTPException):
    def __init__(self, required_permission: str, user_role: str = None):
        detail = f"Access denied. Required permission: {required_permission}"
        if user_role:
            detail += f". Current role: {user_role}"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class AccountSuspendedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Please contact administrator."
        )

class EmailNotVerifiedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required to access this resource."
        )

# Permission Dependency Functions
async def require_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Require user to be active and not suspended."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    if hasattr(current_user, 'status') and current_user.status != UserStatus.ACTIVE:
        raise AccountSuspendedError()
    
    return current_user

async def require_verified_user(
    current_user: UserResponse = Depends(require_active_user)
) -> UserResponse:
    """Require user to have verified email, except for admin users."""
    # Admin users can bypass email verification requirement
    if hasattr(current_user, 'role') and current_user.role == UserRole.ADMIN:
        logger.info(f"Admin user {current_user.email} bypassing email verification")
        return current_user
    
    # DEVELOPMENT: Allow members to bypass email verification for now
    if hasattr(current_user, 'role') and current_user.role == UserRole.MEMBER:
        logger.info(f"DEVELOPMENT: Member user {current_user.email} bypassing email verification")
        return current_user
    
    # For other roles, check email verification
    email_verified = getattr(current_user, 'email_verified', True)
    logger.info(f"Email verification check for {current_user.email}: {email_verified}")
    
    if not email_verified:
        logger.error(f"User {current_user.email} failed email verification check")
        raise EmailNotVerifiedError()
    
    return current_user

async def require_admin_user(
    current_user: UserResponse = Depends(require_verified_user)
) -> UserResponse:
    """Require user to have admin privileges."""
    if not hasattr(current_user, 'role') or current_user.role != UserRole.ADMIN:
        raise InsufficientPermissionsError("admin", getattr(current_user, 'role', 'unknown'))
    
    logger.info(f"Admin access granted to user {current_user.email}")
    return current_user

async def require_librarian_user(
    current_user: UserResponse = Depends(require_verified_user)
) -> UserResponse:
    """Require user to have librarian or admin privileges."""
    if not hasattr(current_user, 'role') or current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise InsufficientPermissionsError("librarian or admin", getattr(current_user, 'role', 'unknown'))
    
    logger.info(f"Librarian access granted to user {current_user.email}")
    return current_user

async def require_member_user(
    current_user: UserResponse = Depends(require_verified_user)
) -> UserResponse:
    """Require user to have member privileges or higher."""
    logger.info(f"RBAC Check - User: {current_user.email}, Role: {getattr(current_user, 'role', 'NO_ROLE')}")
    
    if not hasattr(current_user, 'role'):
        logger.error(f"User {current_user.email} has no role attribute")
        raise InsufficientPermissionsError("member or higher", "no role")
    
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.MEMBER]:
        logger.error(f"User {current_user.email} has insufficient role: {current_user.role}")
        raise InsufficientPermissionsError("member or higher", str(current_user.role))
    
    logger.info(f"RBAC Success - User {current_user.email} with role {current_user.role} granted access")
    return current_user

# Permission Checking Functions
def check_permission(user: UserResponse, permission: str) -> bool:
    """Check if user has specific permission."""
    if not hasattr(user, 'has_permission'):
        # Fallback permission checking
        role_permissions = {
            UserRole.ADMIN: ['admin', 'manage_books', 'manage_authors', 'manage_users', 'admin_panel'],
            UserRole.LIBRARIAN: ['librarian', 'manage_books', 'manage_authors', 'admin_panel'],
            UserRole.MEMBER: ['create_review', 'vote_reviews', 'borrow_books'],
            UserRole.GUEST: []
        }
        user_role = getattr(user, 'role', UserRole.GUEST)
        return permission in role_permissions.get(user_role, [])
    
    return user.has_permission(permission)

def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs or function signature
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, UserResponse):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not check_permission(current_user, permission):
                raise InsufficientPermissionsError(permission, getattr(current_user, 'role', 'unknown'))
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Resource Ownership Dependencies
async def require_resource_owner_or_admin(
    resource_user_id: int,
    current_user: UserResponse = Depends(require_active_user)
) -> UserResponse:
    """Require user to be the resource owner or admin."""
    if current_user.id != resource_user_id and not check_permission(current_user, 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only access your own resources."
        )
    return current_user

def create_ownership_dependency(resource_id_param: str = "resource_id"):
    """Create a dependency that checks resource ownership."""
    async def check_ownership(
        resource_id: int,
        current_user: UserResponse = Depends(require_active_user),
        db: Session = Depends(get_db)
    ) -> UserResponse:
        # This would need to be customized per resource type
        return await require_resource_owner_or_admin(resource_id, current_user)
    
    return check_ownership

# Role-based Dependencies Factory
class RBACDependencies:
    """Factory class for creating RBAC dependencies."""
    
    @staticmethod
    def require_roles(allowed_roles: List[UserRole]):
        """Create dependency that requires one of the specified roles."""
        async def check_roles(
            current_user: UserResponse = Depends(require_verified_user)
        ) -> UserResponse:
            user_role = getattr(current_user, 'role', UserRole.GUEST)
            if user_role not in allowed_roles:
                allowed_roles_str = ", ".join([role.value for role in allowed_roles])
                raise InsufficientPermissionsError(
                    f"one of: {allowed_roles_str}", 
                    user_role.value if hasattr(user_role, 'value') else str(user_role)
                )
            return current_user
        
        return check_roles
    
    @staticmethod
    def require_permissions(required_permissions: List[str], require_all: bool = True):
        """Create dependency that requires specific permissions."""
        async def check_permissions(
            current_user: UserResponse = Depends(require_verified_user)
        ) -> UserResponse:
            user_permissions = getattr(current_user, 'permissions', [])
            
            if require_all:
                missing_permissions = [p for p in required_permissions if p not in user_permissions]
                if missing_permissions:
                    raise InsufficientPermissionsError(f"all of: {', '.join(required_permissions)}")
            else:
                has_any_permission = any(p in user_permissions for p in required_permissions)
                if not has_any_permission:
                    raise InsufficientPermissionsError(f"any of: {', '.join(required_permissions)}")
            
            return current_user
        
        return check_permissions

# Convenience Dependencies
require_admin = RBACDependencies.require_roles([UserRole.ADMIN])
require_librarian_or_admin = RBACDependencies.require_roles([UserRole.ADMIN, UserRole.LIBRARIAN])
require_member_or_higher = RBACDependencies.require_roles([UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.MEMBER])

# Book Management Permissions
require_book_management = RBACDependencies.require_permissions(['manage_books'])
require_author_management = RBACDependencies.require_permissions(['manage_authors'])
require_user_management = RBACDependencies.require_permissions(['manage_users'])

# Review Permissions
require_review_creation = RBACDependencies.require_permissions(['create_review'])
require_review_voting = RBACDependencies.require_permissions(['vote_reviews'])

# Admin Panel Access
require_admin_panel_access = RBACDependencies.require_permissions(['admin_panel'])

# Audit Logging
def log_access_attempt(
    user: UserResponse, 
    resource: str, 
    action: str, 
    success: bool = True,
    details: str = None
):
    """Log access attempts for audit purposes."""
    status_str = "SUCCESS" if success else "DENIED"
    log_message = f"ACCESS {status_str}: User {user.email} ({user.role}) attempted {action} on {resource}"
    
    if details:
        log_message += f" - {details}"
    
    if success:
        logger.info(log_message)
    else:
        logger.warning(log_message)

# Permission Middleware
class PermissionMiddleware:
    """Middleware for automatic permission checking and logging."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # This would be implemented as actual ASGI middleware
        # For now, it's a placeholder for the concept
        await self.app(scope, receive, send)
