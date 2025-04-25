"""
Alembic migration: Add notes field to consents table
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('consents', sa.Column('notes', sa.String(), nullable=True))

def downgrade():
    op.drop_column('consents', 'notes')
