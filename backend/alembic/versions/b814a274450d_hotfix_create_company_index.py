"""hotfix create company_index

Revision ID: b814a274450d
Revises: 40df02823063
Create Date: 2025-12-21 18:35:41.813770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b814a274450d'
down_revision: Union[str, Sequence[str], None] = '40df02823063'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "company_index",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="user_input"),
        sa.Column("popularity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("normalized_name", name="uq_company_index_normalized_name"),
    )
    op.create_index("ix_company_index_normalized_name", "company_index", ["normalized_name"], unique=False)

def downgrade():
    op.drop_index("ix_company_index_normalized_name", table_name="company_index")
    op.drop_table("company_index")
