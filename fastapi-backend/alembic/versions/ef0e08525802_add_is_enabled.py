"""add_is_enabled

Revision ID: ef0e08525802
Revises: a80f3e7d07ec
Create Date: 2026-01-10 01:05:11.870469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef0e08525802'
down_revision: Union[str, Sequence[str], None] = 'a80f3e7d07ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_enabled to chargers
    op.add_column('chargers', sa.Column('is_enabled', sa.Boolean(), server_default='false', nullable=False))
    
    # Add is_enabled to rfid_cards
    op.add_column('rfid_cards', sa.Column('is_enabled', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('rfid_cards', 'is_enabled')
    op.drop_column('chargers', 'is_enabled')
