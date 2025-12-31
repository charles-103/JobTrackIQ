"""add jd processing fields

Revision ID: add_jd_processing
Revises: 40df02823063
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_jd_processing'
down_revision = '40df02823063'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加处理后的JD文本字段
    op.add_column('job_postings', sa.Column('processed_jd', sa.Text(), nullable=True))
    
    # 添加关键技能字段（使用JSON数组存储）
    op.add_column('job_postings', sa.Column('key_skills', postgresql.ARRAY(sa.String()), nullable=True))
    
    # 添加索引以便搜索
    op.create_index('ix_job_postings_key_skills', 'job_postings', ['key_skills'], postgresql_using='gin')


def downgrade() -> None:
    op.drop_index('ix_job_postings_key_skills', table_name='job_postings')
    op.drop_column('job_postings', 'key_skills')
    op.drop_column('job_postings', 'processed_jd')






