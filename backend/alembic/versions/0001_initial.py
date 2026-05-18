"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE roletype AS ENUM ('ADMIN', 'EDITOR', 'MINISTRY_LEAD', 'STAFF', 'MEMBER')")
    op.execute("CREATE TYPE prayerstatus AS ENUM ('ACTIVE', 'CLOSED')")
    op.execute("CREATE TYPE priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')")


def downgrade() -> None:
    op.execute('DROP TYPE IF EXISTS priority')
    op.execute('DROP TYPE IF EXISTS prayerstatus')
    op.execute('DROP TYPE IF EXISTS roletype')
