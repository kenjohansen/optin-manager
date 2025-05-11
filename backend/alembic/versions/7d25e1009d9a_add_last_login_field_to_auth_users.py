"""add_last_login_field_to_auth_users

Revision ID: 7d25e1009d9a
Revises: df0fd22ee051
Create Date: 2025-05-11 11:35:15.014901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d25e1009d9a'
down_revision: Union[str, None] = 'df0fd22ee051'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add only the last_login field to auth_users table
    with op.batch_alter_table('auth_users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    
    # We're purposely ignoring the type changes detected by autogenerate
    # as they may cause issues and we only want to add the last_login field


def downgrade() -> None:
    """Downgrade schema."""
    # Simply remove the last_login column from auth_users table
    with op.batch_alter_table('auth_users', schema=None) as batch_op:
        batch_op.drop_column('last_login')
