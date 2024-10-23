"""Event Logs Addition + Edits

Revision ID: 988223dcc93a
Revises: d84797841bc3
Create Date: 2024-10-23 00:14:05.355350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '988223dcc93a'
down_revision: Union[str, None] = 'd84797841bc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'event',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('is_new', sa.Boolean(), nullable=False, default=True),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('normal_side', sa.String(150), nullable=True),
        sa.Column('category', sa.String(150), nullable=True),
        sa.Column('subcategory', sa.String(150), nullable=True),
        sa.Column('initial_balance', sa.Float(), default=0.0, nullable=False),
        sa.Column('debit', sa.Float(), default=0.0, nullable=False),
        sa.Column('credit', sa.Float(), default=0.0, nullable=False),
        sa.Column('balance', sa.Float(), default=0.0, nullable=False),
        sa.Column('order', sa.Integer(), default=0, nullable=True),
        sa.Column('statement', sa.String(150), nullable=True),
        sa.Column('comment', sa.String(150), nullable=True),
        sa.Column('create_date', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('modify_date', sa.DateTime(), nullable=True, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id'))
    )
    # pass

def downgrade() -> None:
    op.drop_table('event')
