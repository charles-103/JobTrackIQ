"""init

Revision ID: 1021854dee29
Revises: 6d5d3ffad3e3
Create Date: 2025-12-15 23:21:04.442199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1021854dee29'
down_revision: Union[str, Sequence[str], None] = '6d5d3ffad3e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
