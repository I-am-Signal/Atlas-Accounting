"""Initial Migration

Revision ID: a55fc2b140b0
Revises: 
Create Date: 2024-10-02 15:34:17.555390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

# revision identifiers, used by Alembic.
revision: str = 'a55fc2b140b0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
    sa.Column('is_activated', sa.BOOLEAN(), nullable=True),
    sa.Column('username', sa.VARCHAR(length=150), nullable=True),
    sa.Column('email', sa.VARCHAR(length=150), nullable=True),
    sa.Column('first_name', sa.VARCHAR(length=150), nullable=True),
    sa.Column('last_name', sa.VARCHAR(length=150), nullable=True),
    sa.Column('addr_line_1', sa.VARCHAR(length=200), nullable=True),
    sa.Column('addr_line_2', sa.VARCHAR(length=200), nullable=True),
    sa.Column('city', sa.VARCHAR(length=200), nullable=True),
    sa.Column('county', sa.VARCHAR(length=200), nullable=True),
    sa.Column('state', sa.VARCHAR(length=2), nullable=True),
    sa.Column('dob', sa.DATE(), nullable=True),
    sa.Column('role', sa.VARCHAR(length=13), nullable=True),
    sa.Column('company_id', sa.INTEGER(), nullable=True),
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('create_date', sa.DATETIME(), nullable=True),
    sa.Column('modify_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('suspension',
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('suspension_start_date', sa.DATETIME(), nullable=True),
    sa.Column('suspension_end_date', sa.DATETIME(), nullable=True),
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('create_date', sa.DATETIME(), nullable=True),
    sa.Column('modify_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company',
    sa.Column('creator_of_company', sa.INTEGER(), nullable=True),
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('create_date', sa.DATETIME(), nullable=True),
    sa.Column('modify_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['creator_of_company'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('credential',
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('password', sa.VARCHAR(length=150), nullable=True),
    sa.Column('failedAttempts', sa.INTEGER(), nullable=True),
    sa.Column('expirationDate', sa.DATETIME(), nullable=True),
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('create_date', sa.DATETIME(), nullable=True),
    sa.Column('modify_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
def downgrade() -> None:
    op.drop_table('Suspension')
    op.drop_table('Company')
    op.drop_table('Credential')
    op.drop_table('user')
