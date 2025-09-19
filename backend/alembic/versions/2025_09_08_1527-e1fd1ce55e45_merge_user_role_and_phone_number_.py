"""Merge user role and phone number migrations

Revision ID: e1fd1ce55e45
Revises: d468d0f5e90f, 5b276ca49fbc
Create Date: 2025-09-08 15:27:22.261891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1fd1ce55e45'
down_revision: Union[str, Sequence[str], None] = ('d468d0f5e90f', '5b276ca49fbc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
