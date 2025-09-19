"""Add Librarian and Guest roles to users table

Revision ID: 5b276ca49fbc
Revises: d468d0f5e90f
Create Date: 2025-09-08 15:26:05.444402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b276ca49fbc'
down_revision: Union[str, Sequence[str], None] = 'f2c44b2f35d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add LIBRARIAN and GUEST to the role enum
    op.execute("ALTER TABLE users MODIFY COLUMN role ENUM('ADMIN','MEMBER','LIBRARIAN','GUEST') NOT NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert to original enum values
    op.execute("ALTER TABLE users MODIFY COLUMN role ENUM('ADMIN','MEMBER') NOT NULL")
