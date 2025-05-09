"""adiciona affiliate_store

Revision ID: 36500326412b
Revises: a2bc00bfdb17
Create Date: 2025-05-06 19:09:43.911236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36500326412b'
down_revision: Union[str, None] = 'a2bc00bfdb17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('affiliate_stores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('platform', sa.String(), nullable=False),
    sa.Column('api_credentials', sa.JSON(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_affiliate_stores_id'), 'affiliate_stores', ['id'], unique=False)
    op.create_index(op.f('ix_affiliate_stores_name'), 'affiliate_stores', ['name'], unique=False)
    op.create_index(op.f('ix_affiliate_stores_platform'), 'affiliate_stores', ['platform'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_affiliate_stores_platform'), table_name='affiliate_stores')
    op.drop_index(op.f('ix_affiliate_stores_name'), table_name='affiliate_stores')
    op.drop_index(op.f('ix_affiliate_stores_id'), table_name='affiliate_stores')
    op.drop_table('affiliate_stores')
    # ### end Alembic commands ###
