#!/usr/bin/env python3
"""
Command-line interface for database migration management.
"""
import argparse
import sys
import json
from pathlib import Path
from app.utils.migrations import MigrationManager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Database Migration Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check migration status")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message/description")
    create_parser.add_argument("--no-autogenerate", action="store_true", 
                             help="Create empty migration (no autogenerate)")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("--revision", default="head", 
                               help="Target revision (default: head)")
    upgrade_parser.add_argument("--no-backup", action="store_true",
                               help="Skip backup creation")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")
    downgrade_parser.add_argument("--no-backup", action="store_true",
                                 help="Skip backup creation")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show migration history")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create database backup")
    backup_parser.add_argument("--path", help="Backup file path")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore database from backup")
    restore_parser.add_argument("backup_path", help="Path to backup file")
    
    # Current command
    current_parser = subparsers.add_parser("current", help="Show current revision")
    
    # Head command
    head_parser = subparsers.add_parser("head", help="Show head revision")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        migration_manager = MigrationManager()
        
        if args.command == "status":
            status = migration_manager.check_migration_status()
            print("Migration Status:")
            print(f"  Current Revision: {status['current_revision']}")
            print(f"  Head Revision: {status['head_revision']}")
            print(f"  Up to Date: {status['is_up_to_date']}")
            print(f"  Needs Migration: {status['needs_migration']}")
            if status['pending_migrations']:
                print(f"  Pending Migrations: {len(status['pending_migrations'])}")
                for migration in status['pending_migrations']:
                    print(f"    - {migration}")
        
        elif args.command == "create":
            revision = migration_manager.create_migration(
                args.message, 
                autogenerate=not args.no_autogenerate
            )
            print(f"Created migration: {revision}")
        
        elif args.command == "upgrade":
            if args.no_backup:
                success = migration_manager.upgrade_database(args.revision)
                if success:
                    print(f"Successfully upgraded to {args.revision}")
                else:
                    print("Upgrade failed")
                    sys.exit(1)
            else:
                result = migration_manager.safe_migrate(
                    args.revision, 
                    create_backup=True
                )
                print(f"Migration result: {result['message']}")
                if result.get('backup_path'):
                    print(f"Backup created: {result['backup_path']}")
                if not result['success']:
                    sys.exit(1)
        
        elif args.command == "downgrade":
            if not args.no_backup:
                backup_path = migration_manager.backup_database()
                print(f"Backup created: {backup_path}")
            
            success = migration_manager.downgrade_database(args.revision)
            if success:
                print(f"Successfully downgraded to {args.revision}")
            else:
                print("Downgrade failed")
                sys.exit(1)
        
        elif args.command == "history":
            history = migration_manager.get_migration_history()
            print("Migration History:")
            for item in history:
                marker = "→" if item['is_current'] else " "
                head_marker = "(HEAD)" if item['is_head'] else ""
                print(f"  {marker} {item['revision'][:8]} - {item['message']} {head_marker}")
        
        elif args.command == "backup":
            backup_path = migration_manager.backup_database(args.path)
            print(f"Backup created: {backup_path}")
        
        elif args.command == "restore":
            success = migration_manager.restore_database(args.backup_path)
            if success:
                print(f"Successfully restored from {args.backup_path}")
            else:
                print("Restore failed")
                sys.exit(1)
        
        elif args.command == "current":
            current = migration_manager.get_current_revision()
            print(f"Current revision: {current}")
        
        elif args.command == "head":
            head = migration_manager.get_head_revision()
            print(f"Head revision: {head}")
    
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
