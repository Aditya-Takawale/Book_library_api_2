"""
Migration configuration and constants.
"""
from pathlib import Path
from typing import List, Dict, Any

# Migration settings
MIGRATION_CONFIG = {
    # Database settings
    "connection_timeout": 30,
    "command_timeout": 300,
    "pool_timeout": 10,
    
    # Backup settings
    "backup_enabled": True,
    "backup_retention_days": 30,
    "backup_compression": True,
    
    # Safety settings
    "require_confirmation_for_destructive_ops": True,
    "max_rollback_revisions": 5,
    "dry_run_enabled": True,
    
    # Logging
    "log_migrations": True,
    "log_level": "INFO",
    "log_file": "logs/migrations.log",
    
    # Performance
    "batch_size": 1000,
    "parallel_operations": False,
}

# Environments
ENVIRONMENTS = {
    "development": {
        "backup_enabled": False,
        "require_confirmation": False,
        "auto_upgrade": True,
    },
    "staging": {
        "backup_enabled": True,
        "require_confirmation": False,
        "auto_upgrade": True,
    },
    "production": {
        "backup_enabled": True,
        "require_confirmation": True,
        "auto_upgrade": False,
    }
}

# Migration operations that require special handling
DESTRUCTIVE_OPERATIONS = [
    "DROP TABLE",
    "DROP COLUMN",
    "DROP INDEX",
    "TRUNCATE",
    "DELETE FROM",
]

# Migration file templates
MIGRATION_TEMPLATES = {
    "standard": """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""",
    
    "data_migration": """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    # Create a table representation for data manipulation
    # example_table = table('example',
    #     column('id', Integer),
    #     column('name', String),
    #     column('created_at', DateTime)
    # )
    
    # Data migration logic here
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    # Reverse data migration logic here
    ${downgrades if downgrades else "pass"}
""",
}

# Common migration patterns
MIGRATION_PATTERNS = {
    "add_column": {
        "template": "op.add_column('{table}', sa.Column('{column}', {type}, nullable={nullable}))",
        "rollback": "op.drop_column('{table}', '{column}')"
    },
    "drop_column": {
        "template": "op.drop_column('{table}', '{column}')",
        "rollback": "op.add_column('{table}', sa.Column('{column}', {type}, nullable={nullable}))"
    },
    "create_table": {
        "template": """op.create_table('{table}',
    {columns}
)""",
        "rollback": "op.drop_table('{table}')"
    },
    "add_index": {
        "template": "op.create_index('{index_name}', '{table}', ['{columns}'])",
        "rollback": "op.drop_index('{index_name}', table_name='{table}')"
    }
}

# Pre-migration checks
PRE_MIGRATION_CHECKS = [
    {
        "name": "disk_space",
        "description": "Check available disk space",
        "query": "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB' FROM information_schema.tables WHERE table_schema=DATABASE();",
        "threshold": 1000  # MB
    },
    {
        "name": "active_connections",
        "description": "Check number of active connections",
        "query": "SHOW STATUS LIKE 'Threads_connected';",
        "threshold": 100
    },
    {
        "name": "lock_waits",
        "description": "Check for lock waits",
        "query": "SELECT COUNT(*) FROM information_schema.innodb_locks;",
        "threshold": 0
    }
]

# Post-migration checks
POST_MIGRATION_CHECKS = [
    {
        "name": "table_integrity",
        "description": "Check table integrity",
        "query": "CHECK TABLE {tables};",
    },
    {
        "name": "foreign_key_constraints",
        "description": "Verify foreign key constraints",
        "query": """
        SELECT TABLE_NAME, CONSTRAINT_NAME 
        FROM information_schema.TABLE_CONSTRAINTS 
        WHERE CONSTRAINT_TYPE = 'FOREIGN KEY' 
        AND TABLE_SCHEMA = DATABASE();
        """
    }
]

# Migration hooks
MIGRATION_HOOKS = {
    "pre_upgrade": [],
    "post_upgrade": [],
    "pre_downgrade": [],
    "post_downgrade": []
}

# Custom migration commands
CUSTOM_COMMANDS = {
    "seed": {
        "description": "Seed database with initial data",
        "script": "scripts/seed_data.py"
    },
    "cleanup": {
        "description": "Clean up temporary migration data",
        "script": "scripts/cleanup_migration_data.py"
    },
    "validate": {
        "description": "Validate database schema and data",
        "script": "scripts/validate_database.py"
    }
}
