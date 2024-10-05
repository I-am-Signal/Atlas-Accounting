"""Req 1 + pfp stuff

Revision ID: 5743480fd1b7
Revises: a55fc2b140b0
Create Date: 2024-10-04 23:03:01.141612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5743480fd1b7'
down_revision: Union[str, None] = 'a55fc2b140b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('suspension', sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id')))
    
    op.create_table(
        'account',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('account_number', sa.Integer(), nullable=False),
        sa.Column('account_name', sa.String(150), nullable=False),
        sa.Column('account_desc', sa.String(500), nullable=True),
        sa.Column('normal_side', sa.String(150), nullable=True),
        sa.Column('account_category', sa.String(150), nullable=True),
        sa.Column('account_subcat', sa.String(150), nullable=True),
        sa.Column('initial_balance', sa.Float(), default=0.0, nullable=False),
        sa.Column('debit', sa.Float(), default=0.0, nullable=False),
        sa.Column('credit', sa.Float(), default=0.0, nullable=False),
        sa.Column('balance', sa.Float(), default=0.0, nullable=False),
        sa.Column('order', sa.Integer(), default=0, nullable=True),
        sa.Column('statement', sa.String(150), nullable=True),
        sa.Column('comment', sa.String(150), nullable=True),
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('create_date', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('modify_date', sa.DateTime(), nullable=True, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id'))
    )
    
    op.create_table(
        'image',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(150), nullable=False),
        sa.Column('file_mime', sa.String(1000), nullable=False),
        sa.Column('file_data', sa.BLOB(), nullable=False),
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('create_date', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('modify_date', sa.DateTime(), nullable=True, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
    )

def downgrade() -> None:
    op.drop_table('image')
    op.drop_table('account')
    op.drop_column('suspension', 'created_by')