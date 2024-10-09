"""Additions for Accounts

Revision ID: d84797841bc3
Revises: 0cbf815b5c6f
Create Date: 2024-10-08 22:56:47.957463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd84797841bc3'
down_revision: Union[str, None] = '0cbf815b5c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('account') as batch_op:
        batch_op.add_column(sa.Column('company_id', sa.Integer()))
        batch_op.create_foreign_key(
            'fk_account_company_id',
            'company',
            ['company_id'],
            ['id']
        )
        batch_op.add_column(sa.Column('company_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_account_company_id', 
            'company', 
            ['company_id'], 
            ['id']
        )
        batch_op.add_column(sa.Column('is_activated', sa.Boolean(), nullable=False, default=False))
    op.create_table(
        'journal_entry',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status', sa.String(length=150), nullable=False, default='pending'),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('company.id', name='fk_journal_entry_company_id'), nullable=False),
        sa.Column('create_date', sa.DateTime(), default=sa.func.now()),
        sa.Column('modify_date', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id', name='fk_journal_entry_created_by'))
    )
    op.create_table(
        'transaction',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('journal_entry_id', sa.Integer(), sa.ForeignKey('journal_entry.id', name='fk_transaction_journal_entry_id'), nullable=False),
        sa.Column('side_for_transaction', sa.String(length=150), nullable=False),
        sa.Column('account_number', sa.Integer(), sa.ForeignKey('account.number', name='fk_transaction_account_number'), nullable=False),
        sa.Column('amount_changing', sa.Float(), nullable=False),
        sa.Column('create_date', sa.DateTime(), default=sa.func.now()),
        sa.Column('modify_date', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id', name='fk_transaction_created_by'))
    )
    

def downgrade() -> None:
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_constraint('fk_account_company_id', type_='foreignkey')
        batch_op.drop_column('company_id')
        batch_op.drop_column('is_activated')
    op.drop_table('transaction')
    op.drop_table('journal_entry')