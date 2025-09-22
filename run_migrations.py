#!/usr/bin/env python3
"""
Railway migration runner script
"""
import os
import sys
sys.path.append('backend')

from app.utils.migrations import MigrationManager

def main():
    print("🚀 Starting Railway migration...")
    
    try:
        migration_manager = MigrationManager()
        
        # Check current status
        status = migration_manager.check_migration_status()
        print(f"Current revision: {status['current_revision']}")
        print(f"Head revision: {status['head_revision']}")
        print(f"Pending migrations: {len(status['pending_migrations'])}")
        
        if status['needs_migration']:
            print("📦 Running migrations...")
            success = migration_manager.upgrade_database("head")
            
            if success:
                print("✅ Migrations completed successfully!")
                new_status = migration_manager.check_migration_status()
                print(f"New revision: {new_status['current_revision']}")
            else:
                print("❌ Migration failed!")
                return 1
        else:
            print("✅ Database is already up to date!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
