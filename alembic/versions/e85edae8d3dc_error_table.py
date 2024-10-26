"""error table

Revision ID: e85edae8d3dc
Revises: 584559067e64
Create Date: 2024-10-25 21:40:32.647963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e85edae8d3dc'
down_revision: Union[str, None] = '584559067e64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('error',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('create_date', sa.DATETIME(), nullable=True),
    sa.Column('modify_date', sa.DATETIME(), nullable=True),
    sa.Column('errorMessage', sa.String(150), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('error')