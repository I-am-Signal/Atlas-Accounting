"""altering account table

Revision ID: 0cbf815b5c6f
Revises: 5743480fd1b7
Create Date: 2024-10-05 17:49:23.694420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cbf815b5c6f'
down_revision: Union[str, None] = '5743480fd1b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE account
        SET created_by = user_id
    """)
    with op.batch_alter_table('account') as batch_op:
        batch_op.drop_column('user_id')
        batch_op.alter_column('normal_side', existing_type=sa.String(150), type_=sa.String(6), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('account') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_account_user_id',
            'user',
            ['user_id'],
            ['id']
        )
        batch_op.alter_column('normal_side', existing_type=sa.String(6), type=sa.String(150), nullable=True)
    op.execute("""
        UPDATE account
        SET user_id = created_by
    """)
    op.execute("""
        UPDATE account
        SET created_by = NULL
    """)
    