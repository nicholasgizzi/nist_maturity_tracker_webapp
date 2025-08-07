"""Add status column to risks

Revision ID: 79af8e997644
Revises: ef1cd37a0a2e
Create Date: 2025-08-07 13:22:41.297089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79af8e997644'
down_revision = 'ef1cd37a0a2e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('risks', sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'MITIGATED', 'ACCEPTED', name='riskstatus'), nullable=False, server_default='OPEN'))
    op.execute("UPDATE risks SET status='OPEN'")
    # if you want to set default for existing rows, use server_default
def downgrade():
    op.drop_column('risks', 'status')
    # ### end Alembic commands ###
