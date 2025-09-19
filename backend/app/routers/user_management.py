"""
Enhanced user management with Role-Based Access Control.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserRegistration, UserRole, UserStatus
from app.services.user_service import UserService
from app.utils.rbac import (
    require_admin_user,
    require_librarian_user,
    require_member_user,
    log_access_attempt
)
from app.utils.dependencies import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger("UserManagement")

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user's profile information."""
    log_access_attempt(current_user, "users", "view_profile", True)
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information."""
    try:
        # Users can only update certain fields about themselves
        allowed_updates = UserUpdate(
            first_name=user_update.first_name,
            last_name=user_update.last_name
        )
        
        updated_user = UserService.update_user(db, current_user.id, allowed_updates)
        
        log_access_attempt(current_user, "users", "update_profile", True)
        logger.info(f"User {current_user.email} updated their profile")
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        log_access_attempt(current_user, "users", "update_profile", False, str(e))
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile")

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)."""
    try:
        users = UserService.get_all_users(db, role=role, status=status, skip=skip, limit=limit)
        
        log_access_attempt(current_user, "users", "list_all", True, f"Retrieved {len(users)} users")
        return [UserResponse.from_orm(user) for user in users]
        
    except Exception as e:
        log_access_attempt(current_user, "users", "list_all", False, str(e))
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch users")

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserRegistration,
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)."""
    try:
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
        
        new_user = UserService.create_user(db, user_data)
        
        log_access_attempt(current_user, "users", "create", True, f"Created user {user_data.email}")
        logger.info(f"Admin {current_user.email} created new user: {user_data.email}")
        
        return UserResponse.from_orm(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        log_access_attempt(current_user, "users", "create", False, str(e))
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)."""
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        log_access_attempt(current_user, "users", "view_user", True, f"User {user_id}")
        return UserResponse.from_orm(user)
        
    except HTTPException:
        log_access_attempt(current_user, "users", "view_user", False, f"User {user_id} not found")
        raise
    except Exception as e:
        log_access_attempt(current_user, "users", "view_user", False, str(e))
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch user")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)."""
    try:
        # Prevent admins from downgrading their own role
        if user_id == current_user.id and user_update.role and user_update.role != UserRole.ADMIN:
            log_access_attempt(current_user, "users", "update_user", False, "Cannot downgrade own admin role")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot downgrade your own admin role"
            )
        
        updated_user = UserService.update_user(db, user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        log_access_attempt(current_user, "users", "update_user", True, f"User {user_id}")
        logger.info(f"Admin {current_user.email} updated user {user_id}")
        
        return UserResponse.from_orm(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        log_access_attempt(current_user, "users", "update_user", False, str(e))
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")

@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Suspend a user account (admin only)."""
    try:
        # Prevent admins from suspending themselves
        if user_id == current_user.id:
            log_access_attempt(current_user, "users", "suspend_user", False, "Cannot suspend own account")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot suspend your own account"
            )
        
        user_update = UserUpdate(status=UserStatus.SUSPENDED)
        updated_user = UserService.update_user(db, user_id, user_update)
        
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        log_access_attempt(current_user, "users", "suspend_user", True, f"User {user_id}")
        logger.warning(f"Admin {current_user.email} suspended user {user_id}")
        
        return {"message": f"User {user_id} has been suspended"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_access_attempt(current_user, "users", "suspend_user", False, str(e))
        logger.error(f"Error suspending user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to suspend user")

@router.post("/{user_id}/reactivate")
async def reactivate_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Reactivate a suspended user account (admin only)."""
    try:
        user_update = UserUpdate(status=UserStatus.ACTIVE)
        updated_user = UserService.update_user(db, user_id, user_update)
        
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        log_access_attempt(current_user, "users", "reactivate_user", True, f"User {user_id}")
        logger.info(f"Admin {current_user.email} reactivated user {user_id}")
        
        return {"message": f"User {user_id} has been reactivated"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_access_attempt(current_user, "users", "reactivate_user", False, str(e))
        logger.error(f"Error reactivating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reactivate user")

@router.post("/{user_id}/promote")
async def promote_user(
    user_id: int,
    new_role: UserRole,
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Promote user to a higher role (admin only)."""
    try:
        # Only allow promotion to valid roles
        if new_role not in [UserRole.MEMBER, UserRole.LIBRARIAN, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role for promotion"
            )
        
        user_update = UserUpdate(role=new_role)
        updated_user = UserService.update_user(db, user_id, user_update)
        
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        log_access_attempt(current_user, "users", "promote_user", True, f"User {user_id} to {new_role}")
        logger.info(f"Admin {current_user.email} promoted user {user_id} to {new_role}")
        
        return {"message": f"User {user_id} has been promoted to {new_role}"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_access_attempt(current_user, "users", "promote_user", False, str(e))
        logger.error(f"Error promoting user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to promote user")

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user account (admin only) - soft delete."""
    try:
        # Prevent admins from deleting themselves
        if user_id == current_user.id:
            log_access_attempt(current_user, "users", "delete_user", False, "Cannot delete own account")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot delete your own account"
            )
        
        # Soft delete by setting status to DELETED
        user_update = UserUpdate(status=UserStatus.DELETED, is_active=False)
        deleted_user = UserService.update_user(db, user_id, user_update)
        
        if not deleted_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        log_access_attempt(current_user, "users", "delete_user", True, f"User {user_id}")
        logger.warning(f"Admin {current_user.email} deleted user {user_id}")
        
        return {"message": f"User {user_id} has been deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_access_attempt(current_user, "users", "delete_user", False, str(e))
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")

@router.get("/roles/permissions")
async def get_role_permissions(
    current_user: UserResponse = Depends(require_member_user)
):
    """Get role-permission mapping information."""
    role_permissions = {
        UserRole.ADMIN: [
            "admin", "manage_books", "manage_authors", "manage_users", 
            "admin_panel", "create_review", "vote_reviews", "borrow_books"
        ],
        UserRole.LIBRARIAN: [
            "librarian", "manage_books", "manage_authors", "admin_panel",
            "create_review", "vote_reviews", "borrow_books"
        ],
        UserRole.MEMBER: [
            "create_review", "vote_reviews", "borrow_books"
        ],
        UserRole.GUEST: []
    }
    
    log_access_attempt(current_user, "users", "view_permissions", True)
    return {
        "role_permissions": role_permissions,
        "current_user_role": current_user.role,
        "current_user_permissions": current_user.permissions
    }

@router.get("/activity/statistics")
async def get_user_activity_statistics(
    current_user: UserResponse = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """Get user activity statistics (admin only)."""
    try:
        # Get user counts by role and status
        stats = UserService.get_user_statistics(db)
        
        log_access_attempt(current_user, "users", "view_statistics", True)
        return stats
        
    except Exception as e:
        log_access_attempt(current_user, "users", "view_statistics", False, str(e))
        logger.error(f"Error fetching user statistics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch statistics")
