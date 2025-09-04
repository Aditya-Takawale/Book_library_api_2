"""
Migration utilities for database schema management.
"""
import os
import sys
import subprocess
from typing import List, Optional
from pathlib import Path
import logging
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from app.config import settings

logger = logging.getLogger(__name__)

class MigrationManager:
    """
    Comprehensive migration management system with Alembic integration.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.alembic_cfg_path = self.project_root / "alembic.ini"
        self.config = Config(str(self.alembic_cfg_path))
        self.engine = create_engine(settings.DATABASE_URL)
        
    def get_current_revision(self) -> Optional[str]:
        """Get the current database revision."""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Error getting current revision: {e}")
            return None
    
    def get_head_revision(self) -> Optional[str]:
        """Get the latest migration revision."""
        try:
            script = ScriptDirectory.from_config(self.config)
            return script.get_current_head()
        except Exception as e:
            logger.error(f"Error getting head revision: {e}")
            return None
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations."""
        try:
            current = self.get_current_revision()
            script = ScriptDirectory.from_config(self.config)
            
            if current is None:
                # No migrations applied yet, return all migrations
                return [rev.revision for rev in script.walk_revisions()]
            
            pending = []
            for rev in script.walk_revisions("head", current):
                if rev.revision != current:
                    pending.append(rev.revision)
            
            return pending
        except Exception as e:
            logger.error(f"Error getting pending migrations: {e}")
            return []
    
    def create_migration(self, message: str, autogenerate: bool = True) -> str:
        """Create a new migration."""
        try:
            if autogenerate:
                command.revision(self.config, message=message, autogenerate=True)
            else:
                command.revision(self.config, message=message)
            
            logger.info(f"Created migration: {message}")
            return self.get_head_revision()
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
            raise
    
    def upgrade_database(self, revision: str = "head") -> bool:
        """Upgrade database to specified revision."""
        try:
            command.upgrade(self.config, revision)
            logger.info(f"Upgraded database to revision: {revision}")
            return True
        except Exception as e:
            logger.error(f"Error upgrading database: {e}")
            return False
    
    def downgrade_database(self, revision: str) -> bool:
        """Downgrade database to specified revision."""
        try:
            command.downgrade(self.config, revision)
            logger.info(f"Downgraded database to revision: {revision}")
            return True
        except Exception as e:
            logger.error(f"Error downgrading database: {e}")
            return False
    
    def get_migration_history(self) -> List[dict]:
        """Get migration history."""
        try:
            script = ScriptDirectory.from_config(self.config)
            current = self.get_current_revision()
            
            history = []
            for rev in script.walk_revisions():
                is_current = rev.revision == current
                history.append({
                    "revision": rev.revision,
                    "message": rev.doc,
                    "is_current": is_current,
                    "is_head": rev.is_head,
                    "down_revision": rev.down_revision
                })
            
            return history
        except Exception as e:
            logger.error(f"Error getting migration history: {e}")
            return []
    
    def check_migration_status(self) -> dict:
        """Check the current migration status."""
        try:
            current = self.get_current_revision()
            head = self.get_head_revision()
            pending = self.get_pending_migrations()
            
            return {
                "current_revision": current,
                "head_revision": head,
                "pending_migrations": pending,
                "is_up_to_date": current == head,
                "needs_migration": len(pending) > 0
            }
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return {
                "current_revision": None,
                "head_revision": None,
                "pending_migrations": [],
                "is_up_to_date": False,
                "needs_migration": False,
                "error": str(e)
            }
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a database backup before migration."""
        try:
            if backup_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_{timestamp}.sql"
            
            # Extract database connection details
            from urllib.parse import urlparse
            parsed = urlparse(settings.DATABASE_URL)
            
            cmd = [
                "mysqldump",
                f"--host={parsed.hostname}",
                f"--port={parsed.port or 3306}",
                f"--user={parsed.username}",
                parsed.path.lstrip('/'),  # database name
                f"--result-file={backup_path}"
            ]
            
            if parsed.password:
                cmd.insert(-2, f"--password={parsed.password}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup created: {backup_path}")
                return backup_path
            else:
                logger.error(f"Backup failed: {result.stderr}")
                raise Exception(f"Backup failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(settings.DATABASE_URL)
            
            cmd = [
                "mysql",
                f"--host={parsed.hostname}",
                f"--port={parsed.port or 3306}",
                f"--user={parsed.username}",
                parsed.path.lstrip('/'),  # database name
            ]
            
            if parsed.password:
                cmd.append(f"--password={parsed.password}")
            
            with open(backup_path, 'r') as backup_file:
                result = subprocess.run(cmd, stdin=backup_file, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database restored from: {backup_path}")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
    
    def safe_migrate(self, target_revision: str = "head", create_backup: bool = True) -> dict:
        """Safely migrate database with backup and rollback capabilities."""
        backup_path = None
        original_revision = self.get_current_revision()
        
        try:
            # Create backup if requested
            if create_backup:
                backup_path = self.backup_database()
            
            # Perform migration
            success = self.upgrade_database(target_revision)
            
            if success:
                return {
                    "success": True,
                    "message": f"Migration successful to {target_revision}",
                    "backup_path": backup_path,
                    "original_revision": original_revision,
                    "current_revision": self.get_current_revision()
                }
            else:
                return {
                    "success": False,
                    "message": "Migration failed",
                    "backup_path": backup_path,
                    "original_revision": original_revision
                }
        
        except Exception as e:
            logger.error(f"Migration error: {e}")
            
            # Attempt rollback if we have the original revision
            if original_revision:
                logger.info("Attempting rollback...")
                rollback_success = self.downgrade_database(original_revision)
                
                return {
                    "success": False,
                    "message": f"Migration failed: {e}",
                    "backup_path": backup_path,
                    "original_revision": original_revision,
                    "rollback_attempted": True,
                    "rollback_success": rollback_success
                }
            
            return {
                "success": False,
                "message": f"Migration failed: {e}",
                "backup_path": backup_path,
                "original_revision": original_revision,
                "rollback_attempted": False
            }
