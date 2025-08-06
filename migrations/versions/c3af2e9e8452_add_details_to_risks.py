"""Add details to risks

Revision ID: c3af2e9e8452
Revises: b88469dac3f4
Create Date: 2025-08-06 16:25:07.108651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3af2e9e8452'
down_revision = 'b88469dac3f4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('risks', sa.Column('details', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('risks', 'details')