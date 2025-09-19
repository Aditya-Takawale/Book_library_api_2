#!/bin/bash
"""
Production deployment script with migration support.
This script handles database migrations during deployment with safety checks.
"""

set -e  # Exit on any error

# Configuration
APP_DIR="/path/to/your/app"
BACKUP_DIR="/path/to/backups"
LOG_FILE="/var/log/deployment.log"
VENV_PATH="/path/to/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if we're in the right directory
check_environment() {
    log "Checking deployment environment..."
    
    if [ ! -f "backend/app/main.py" ]; then
        error "backend/app/main.py not found. Are you in the correct directory?"
        exit 1
    fi
    
    if [ ! -f "backend/alembic.ini" ]; then
        error "backend/alembic.ini not found. Migration system not initialized."
        exit 1
    fi
    
    log "Environment check passed."
}

# Activate virtual environment
activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        log "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"
    else
        warning "Virtual environment not found at $VENV_PATH"
    fi
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    
    python -c "
from app.core.db import engine
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"
    
    if [ $? -ne 0 ]; then
        error "Database connectivity check failed."
        exit 1
    fi
    
    log "Database connectivity confirmed."
}

# Create backup
create_backup() {
    log "Creating database backup..."
    
    mkdir -p "$BACKUP_DIR"
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="$BACKUP_DIR/backup_$timestamp.sql"
    
    python migration_cli.py backup --path "$backup_file"
    
    if [ $? -eq 0 ]; then
        log "Backup created: $backup_file"
        echo "$backup_file" > "$BACKUP_DIR/latest_backup.txt"
    else
        error "Backup creation failed."
        exit 1
    fi
}

# Check migration status
check_migrations() {
    log "Checking migration status..."
    
    python migration_cli.py status > migration_status.tmp
    
    if grep -q "Needs Migration: True" migration_status.tmp; then
        log "Pending migrations detected."
        cat migration_status.tmp
        return 1
    else
        log "Database is up to date."
        rm migration_status.tmp
        return 0
    fi
}

# Apply migrations
apply_migrations() {
    log "Applying database migrations..."
    
    python migration_cli.py upgrade
    
    if [ $? -eq 0 ]; then
        log "Migrations applied successfully."
    else
        error "Migration failed. Starting rollback..."
        rollback_deployment
        exit 1
    fi
}

# Rollback deployment
rollback_deployment() {
    warning "Rolling back deployment..."
    
    if [ -f "$BACKUP_DIR/latest_backup.txt" ]; then
        latest_backup=$(cat "$BACKUP_DIR/latest_backup.txt")
        log "Restoring from backup: $latest_backup"
        
        python migration_cli.py restore "$latest_backup"
        
        if [ $? -eq 0 ]; then
            log "Rollback completed successfully."
        else
            error "Rollback failed. Manual intervention required."
        fi
    else
        error "No backup file found for rollback."
    fi
}

# Update application dependencies
update_dependencies() {
    log "Updating application dependencies..."
    
    pip install -r requirements.txt --upgrade
    
    if [ $? -eq 0 ]; then
        log "Dependencies updated successfully."
    else
        error "Dependency update failed."
        exit 1
    fi
}

# Restart application services
restart_services() {
    log "Restarting application services..."
    
    # Customize these commands based on your deployment setup
    if command -v systemctl &> /dev/null; then
        systemctl restart your-app-service
        systemctl status your-app-service
    elif command -v supervisorctl &> /dev/null; then
        supervisorctl restart your-app
        supervisorctl status your-app
    else
        warning "No service manager found. Please restart your application manually."
    fi
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait for service to start
    sleep 10
    
    # Check if the application is responding
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health || echo "000")
    
    if [ "$response" = "200" ]; then
        log "Health check passed. Application is running."
    else
        error "Health check failed. Response code: $response"
        return 1
    fi
}

# Cleanup old backups (keep last 10)
cleanup_backups() {
    log "Cleaning up old backups..."
    
    cd "$BACKUP_DIR"
    ls -t backup_*.sql | tail -n +11 | xargs -r rm
    
    log "Backup cleanup completed."
}

# Main deployment function
deploy() {
    log "Starting deployment process..."
    
    check_environment
    activate_venv
    check_database
    create_backup
    
    if check_migrations; then
        log "No migrations needed."
    else
        apply_migrations
    fi
    
    update_dependencies
    restart_services
    
    if health_check; then
        log "Deployment completed successfully!"
        cleanup_backups
    else
        error "Deployment failed health check."
        rollback_deployment
        exit 1
    fi
}

# Script entry point
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "rollback")
        rollback_deployment
        ;;
    "backup")
        create_backup
        ;;
    "check")
        check_migrations
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|backup|check|health}"
        exit 1
        ;;
esac
