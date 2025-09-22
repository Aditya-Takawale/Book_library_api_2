"""
Migration management API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.utils.migrations import MigrationManager
from app.utils.dependencies import get_current_user
from app.schemas.user import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/migrations", tags=["Migration Management"])
security = HTTPBearer()

# Pydantic models for API responses
class MigrationStatusResponse(BaseModel):
    current_revision: Optional[str]
    head_revision: Optional[str]
    pending_migrations: List[str]
    is_up_to_date: bool
    needs_migration: bool
    error: Optional[str] = None

class MigrationHistoryItem(BaseModel):
    revision: str
    message: Optional[str]
    is_current: bool
    is_head: bool
    down_revision: Optional[str]

class MigrationRequest(BaseModel):
    message: str
    autogenerate: bool = True

class UpgradeRequest(BaseModel):
    revision: str = "head"
    create_backup: bool = True

class DowngradeRequest(BaseModel):
    revision: str
    create_backup: bool = True

class MigrationResult(BaseModel):
    success: bool
    message: str
    backup_path: Optional[str] = None
    original_revision: Optional[str] = None
    current_revision: Optional[str] = None
    rollback_attempted: Optional[bool] = None
    rollback_success: Optional[bool] = None

class BackupRequest(BaseModel):
    path: Optional[str] = None

class RestoreRequest(BaseModel):
    backup_path: str

# Dependency to check admin privileges
async def require_admin_user(current_user: UserResponse = Depends(get_current_user)):
    """Require admin user for migration operations."""
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required for migration operations"
        )
    return current_user

@router.get("/status", response_model=MigrationStatusResponse)
async def get_migration_status(current_user: UserResponse = Depends(require_admin_user)):
    """Get current migration status."""
    try:
        migration_manager = MigrationManager()
        status = migration_manager.check_migration_status()
        return MigrationStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting migration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[MigrationHistoryItem])
async def get_migration_history(current_user: UserResponse = Depends(require_admin_user)):
    """Get migration history."""
    try:
        migration_manager = MigrationManager()
        history = migration_manager.get_migration_history()
        return [MigrationHistoryItem(**item) for item in history]
    except Exception as e:
        logger.error(f"Error getting migration history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current")
async def get_current_revision(current_user: UserResponse = Depends(require_admin_user)):
    """Get current database revision."""
    try:
        migration_manager = MigrationManager()
        current = migration_manager.get_current_revision()
        return {"current_revision": current}
    except Exception as e:
        logger.error(f"Error getting current revision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/head")
async def get_head_revision(current_user: UserResponse = Depends(require_admin_user)):
    """Get head (latest) revision."""
    try:
        migration_manager = MigrationManager()
        head = migration_manager.get_head_revision()
        return {"head_revision": head}
    except Exception as e:
        logger.error(f"Error getting head revision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_migration(
    request: MigrationRequest,
    current_user: UserResponse = Depends(require_admin_user)
):
    """Create a new migration."""
    try:
        migration_manager = MigrationManager()
        revision = migration_manager.create_migration(
            request.message, 
            autogenerate=request.autogenerate
        )
        return {
            "success": True,
            "message": f"Migration created: {request.message}",
            "revision": revision
        }
    except Exception as e:
        logger.error(f"Error creating migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upgrade", response_model=MigrationResult)
async def upgrade_database(
    request: UpgradeRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(require_admin_user)
):
    """Upgrade database to specified revision."""
    try:
        migration_manager = MigrationManager()
        
        if request.create_backup:
            result = migration_manager.safe_migrate(
                request.revision, 
                create_backup=True
            )
        else:
            success = migration_manager.upgrade_database(request.revision)
            result = {
                "success": success,
                "message": f"Upgraded to {request.revision}" if success else "Upgrade failed",
                "current_revision": migration_manager.get_current_revision()
            }
        
        return MigrationResult(**result)
    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/downgrade", response_model=MigrationResult)
async def downgrade_database(
    request: DowngradeRequest,
    current_user: UserResponse = Depends(require_admin_user)
):
    """Downgrade database to specified revision."""
    try:
        migration_manager = MigrationManager()
        
        backup_path = None
        if request.create_backup:
            backup_path = migration_manager.backup_database()
        
        success = migration_manager.downgrade_database(request.revision)
        
        result = {
            "success": success,
            "message": f"Downgraded to {request.revision}" if success else "Downgrade failed",
            "backup_path": backup_path,
            "current_revision": migration_manager.get_current_revision()
        }
        
        return MigrationResult(**result)
    except Exception as e:
        logger.error(f"Error downgrading database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup")
async def create_backup(
    request: BackupRequest,
    current_user: UserResponse = Depends(require_admin_user)
):
    """Create a database backup."""
    try:
        migration_manager = MigrationManager()
        backup_path = migration_manager.backup_database(request.path)
        return {
            "success": True,
            "message": "Backup created successfully",
            "backup_path": backup_path
        }
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore")
async def restore_backup(
    request: RestoreRequest,
    current_user: UserResponse = Depends(require_admin_user)
):
    """Restore database from backup."""
    try:
        migration_manager = MigrationManager()
        success = migration_manager.restore_database(request.backup_path)
        
        return {
            "success": success,
            "message": f"Restored from {request.backup_path}" if success else "Restore failed"
        }
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
async def get_pending_migrations(current_user: UserResponse = Depends(require_admin_user)):
    """Get list of pending migrations."""
    try:
        migration_manager = MigrationManager()
        pending = migration_manager.get_pending_migrations()
        return {
            "pending_migrations": pending,
            "count": len(pending)
        }
    except Exception as e:
        logger.error(f"Error getting pending migrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upgrade-simple")
async def upgrade_database_simple(
    current_user: UserResponse = Depends(require_admin_user)
):
    """Simple database upgrade without backup (for Railway environment)."""
    try:
        migration_manager = MigrationManager()
        
        # Direct upgrade without backup
        success = migration_manager.upgrade_database("head")
        current_revision = migration_manager.get_current_revision()
        
        return {
            "success": success,
            "message": "Database upgraded successfully" if success else "Database upgrade failed",
            "current_revision": current_revision,
            "backup_path": None
        }
    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        raise HTTPException(status_code=500, detail=str(e))
