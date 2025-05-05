# app/db/migrations/versions/XXXXXX_add_affiliate_url.py
"""add affiliate url

Revision ID: 000001
Revises: previous_revision
Create Date: 2025-05-04 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '000001'
down_revision = 'none'  # Substitua pelo ID da revisão anterior
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('products', sa.Column('affiliate_url', sa.String(), nullable=True))

def downgrade():
    op.drop_column('products', 'affiliate_url')