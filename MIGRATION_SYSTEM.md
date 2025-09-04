# Database Migration System Documentation

## Overview

This Book Library API implements a comprehensive **Alembic-based migration system** that provides:

- **Version Control** for database schema changes
- **Rollback Capabilities** for safe deployments  
- **Automated Backup & Restore** functionality
- **CLI Tools** for migration management
- **API Endpoints** for web-based administration
- **Production Deployment** scripts

## 🚀 Quick Start

### CLI Commands

```bash
# Check migration status
python migration_cli.py status

# Create new migration
python migration_cli.py create "Add user preferences table"

# Apply migrations
python migration_cli.py upgrade

# Rollback to specific revision
python migration_cli.py downgrade <revision_id>

# View migration history
python migration_cli.py history

# Create database backup
python migration_cli.py backup

# Restore from backup
python migration_cli.py restore backup_20250903_160000.sql
```

### Direct Alembic Commands

```bash
# Generate migration with auto-detection
alembic revision --autogenerate -m "Add new features"

# Upgrade to latest
alembic upgrade head

# Downgrade one step
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## 📁 Project Structure

```
/book_library_api/
├── alembic.ini                 # Alembic configuration
├── migration_cli.py            # CLI management tool
├── alembic/
│   ├── env.py                  # Environment configuration
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
│       ├── 001_initial.py
│       └── 002_add_reviews.py
├── app/
│   ├── utils/
│   │   ├── migrations.py       # Migration management class
│   │   └── migration_config.py # Configuration constants
│   └── routers/
│       └── migration.py        # API endpoints
└── scripts/
    └── deploy.sh              # Production deployment script
```

## 🔧 Core Components

### 1. MigrationManager Class

Located in `app/utils/migrations.py`, this class provides:

```python
from app.utils.migrations import MigrationManager

manager = MigrationManager()

# Check status
status = manager.check_migration_status()

# Create migration
revision = manager.create_migration("Add book categories", autogenerate=True)

# Safe migration with backup
result = manager.safe_migrate("head", create_backup=True)

# Get migration history
history = manager.get_migration_history()
```

### 2. CLI Tool

```bash
# All available commands
python migration_cli.py --help

# Status with details
python migration_cli.py status
# Output:
# Migration Status:
#   Current Revision: decb1406ac43
#   Head Revision: 9a385a344ba4
#   Up to Date: False
#   Needs Migration: True
#   Pending Migrations: 1
#     - 9a385a344ba4
```

### 3. API Endpoints

Available at `/admin/migrations/*` (requires admin authentication):

- `GET /admin/migrations/status` - Get migration status
- `GET /admin/migrations/history` - Get migration history
- `POST /admin/migrations/create` - Create new migration
- `POST /admin/migrations/upgrade` - Apply migrations
- `POST /admin/migrations/downgrade` - Rollback migrations
- `POST /admin/migrations/backup` - Create database backup
- `POST /admin/migrations/restore` - Restore from backup

## 🛡️ Safety Features

### Automatic Backups
```python
# Safe migration with automatic backup
result = manager.safe_migrate("head", create_backup=True)

if not result['success']:
    print(f"Migration failed: {result['message']}")
    if result.get('rollback_attempted'):
        print(f"Rollback successful: {result['rollback_success']}")
```

### Pre-Migration Checks
- Disk space validation
- Active connection monitoring  
- Lock wait detection
- Table integrity verification

### Rollback Support
```bash
# Rollback to previous version
python migration_cli.py downgrade -1

# Rollback to specific revision
python migration_cli.py downgrade abc123def456

# Emergency rollback using backup
python migration_cli.py restore backup_20250903_160000.sql
```

## 🎯 Common Use Cases

### 1. Adding a New Column

```bash
# Create migration
python migration_cli.py create "Add user_avatar column to users table"

# Edit the generated migration file if needed
# Apply migration
python migration_cli.py upgrade
```

### 2. Production Deployment

```bash
# Use the deployment script
./scripts/deploy.sh

# Or step by step:
python migration_cli.py backup
python migration_cli.py status
python migration_cli.py upgrade --no-backup  # backup already created
```

### 3. Emergency Rollback

```bash
# Quick rollback to previous version
python migration_cli.py downgrade -1

# Or restore from backup
python migration_cli.py restore backup_20250903_160000.sql
```

### 4. Development Workflow

```python
# 1. Make model changes in app/models/
# 2. Generate migration
python migration_cli.py create "Add book rating system"

# 3. Review generated migration file
# 4. Test migration
python migration_cli.py upgrade

# 5. If issues, rollback
python migration_cli.py downgrade -1
```

## 🔒 Security & Access Control

### Admin-Only API Access
Migration API endpoints require admin privileges:

```python
# Example admin check
async def require_admin_user(current_user: UserResponse = Depends(get_current_user)):
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
```

### Authentication Setup
1. Login via `/auth/login` endpoint
2. Use the Bearer token in API requests
3. Ensure user has admin privileges

## 📊 Monitoring & Health Checks

### Health Endpoint
```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected", 
  "migrations": {
    "current_revision": "decb1406ac43",
    "is_up_to_date": false
  }
}
```

### Migration Status API
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8080/admin/migrations/status
```

## 🚀 Production Deployment

### Using Deploy Script
```bash
./scripts/deploy.sh
```

The deployment script:
1. ✅ Validates environment
2. ✅ Checks database connectivity  
3. ✅ Creates automatic backup
4. ✅ Applies pending migrations
5. ✅ Updates dependencies
6. ✅ Restarts services
7. ✅ Runs health checks
8. ✅ Cleans up old backups

### Manual Deployment
```bash
# 1. Backup database
python migration_cli.py backup

# 2. Check what needs migrating
python migration_cli.py status

# 3. Apply migrations
python migration_cli.py upgrade

# 4. Verify health
curl http://localhost:8080/health
```

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
```

### Alembic Configuration
Edit `alembic.ini` for:
- File naming patterns
- Migration timeout settings
- Backup retention policies

### Migration Settings
Configure in `app/utils/migration_config.py`:
```python
MIGRATION_CONFIG = {
    "backup_enabled": True,
    "backup_retention_days": 30,
    "require_confirmation_for_destructive_ops": True,
    "max_rollback_revisions": 5,
}
```

## 🐛 Troubleshooting

### Common Issues

**1. Migration Conflicts**
```bash
# Check current state
python migration_cli.py status

# If conflicts, merge migrations
alembic merge heads

# Or reset to known good state
python migration_cli.py downgrade <good_revision>
```

**2. Database Connection Issues**
```bash
# Test connectivity
python -c "from app.core.db import engine; engine.connect()"

# Check configuration
echo $DATABASE_URL
```

**3. Permission Errors**
```bash
# Ensure CLI script is executable
chmod +x migration_cli.py
chmod +x scripts/deploy.sh
```

**4. Backup/Restore Issues**
```bash
# Check MySQL tools are available
which mysqldump
which mysql

# Test backup manually
mysqldump -u root library_db > test_backup.sql
```

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python migration_cli.py status
```

## 📝 Migration Best Practices

### 1. **Always Review Generated Migrations**
```python
# Check the generated migration file before applying
# Make sure column defaults are appropriate
# Verify foreign key constraints
```

### 2. **Use Descriptive Messages**
```bash
python migration_cli.py create "Add user_preferences table with JSON settings column"
```

### 3. **Test Migrations Locally First**
```bash
# Create test database
# Apply migration
# Test rollback
# Verify data integrity
```

### 4. **Backup Before Production Changes**
```bash
# Always backup before major migrations
python migration_cli.py backup --path production_backup_$(date +%Y%m%d).sql
```

### 5. **Monitor Migration Performance**
```bash
# Use time command for large migrations
time python migration_cli.py upgrade
```

## 🎉 Success! Your Migration System is Ready

You now have a production-ready database migration system with:

✅ **Version Control** - Track all database changes  
✅ **Rollback Safety** - Undo changes when needed  
✅ **Automated Backups** - Never lose data  
✅ **CLI Tools** - Easy command-line management  
✅ **API Integration** - Web-based administration  
✅ **Production Scripts** - Automated deployment  
✅ **Health Monitoring** - Real-time status checks  

Start using it now:
```bash
python migration_cli.py status
```
