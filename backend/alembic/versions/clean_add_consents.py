"""Add consents table cleanly

Revision ID: clean_add_consents
Revises: 055578f88857
Create Date: 2025-04-24 09:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'clean_add_consents'
down_revision = '055578f88857'
branch_labels = None
depends_on = None


def upgrade():
    # Create consents table directly without modifying other tables
    op.create_table('consents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('optin_id', sa.String(), nullable=True),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True, default='pending'),
        sa.Column('consent_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_id', sa.String(), nullable=True),
        sa.Column('record', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # Add foreign key constraints separately to avoid issues
    with op.batch_alter_table('consents', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_consents_user_id_contacts', 'contacts', ['user_id'], ['id'])
        batch_op.create_foreign_key('fk_consents_optin_id_optins', 'optins', ['optin_id'], ['id'])
        batch_op.create_foreign_key('fk_consents_verification_id_verification_codes', 'verification_codes', ['verification_id'], ['id'])


def downgrade():
    # Drop foreign keys first
    with op.batch_alter_table('consents', schema=None) as batch_op:
        batch_op.drop_constraint('fk_consents_user_id_contacts', type_='foreignkey')
        batch_op.drop_constraint('fk_consents_optin_id_optins', type_='foreignkey')
        batch_op.drop_constraint('fk_consents_verification_id_verification_codes', type_='foreignkey')
    
    # Then drop the table
    op.drop_table('consents')
