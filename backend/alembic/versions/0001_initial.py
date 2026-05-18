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
    op.execute("CREATE TYPE roletype AS ENUM ('admin', 'editor', 'ministry_lead', 'staff', 'member')")
    op.execute("CREATE TYPE prayerstatus AS ENUM ('active', 'closed')")
    op.execute("CREATE TYPE priority AS ENUM ('low', 'medium', 'high', 'critical')")
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('phone_encrypted', sa.LargeBinary(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('twofa_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('twofa_secret_encrypted', sa.LargeBinary(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('name', sa.Enum('admin', 'editor', 'ministry_lead', 'staff', 'member', name='roletype'), unique=True, nullable=False),
    )
    
    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('code', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(255), nullable=False),
    )
    
    # Create role_permissions association table
    op.create_table('role_permissions',
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    )
    
    # Create user_roles association table
    op.create_table('user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    op.execute('DROP TYPE IF EXISTS priority')
    op.execute('DROP TYPE IF EXISTS prayerstatus')
    op.execute('DROP TYPE IF EXISTS roletype')
