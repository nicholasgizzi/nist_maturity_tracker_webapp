"""Normalize existing risk status values

Revision ID: ffe7f04d681b
Revises: 1965899b27ea
Create Date: 2025-08-07 13:45:32.406838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffe7f04d681b'
down_revision = '1965899b27ea'
branch_labels = None
depends_on = None


def upgrade():
    # fix lowercase or space-separated values to match our enum
    op.execute("UPDATE risks SET status = 'OPEN'         WHERE status IS NULL OR LOWER(status) = 'open';")
    op.execute("UPDATE risks SET status = 'IN_PROGRESS' WHERE LOWER(status) = 'in progress';")
    op.execute("UPDATE risks SET status = 'MITIGATED'   WHERE LOWER(status) = 'mitigated';")
    op.execute("UPDATE risks SET status = 'ACCEPTED'    WHERE LOWER(status) = 'accepted';")

def downgrade():
    # (optional) reverse the normalization if you ever downgrade
    op.execute("UPDATE risks SET status = 'Open'         WHERE status = 'OPEN';")
    op.execute("UPDATE risks SET status = 'In Progress' WHERE status = 'IN_PROGRESS';")
    op.execute("UPDATE risks SET status = 'Mitigated'   WHERE status = 'MITIGATED';")
    op.execute("UPDATE risks SET status = 'Accepted'    WHERE status = 'ACCEPTED';")