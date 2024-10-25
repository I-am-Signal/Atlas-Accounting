"""adding comment to journal entry

Revision ID: 584559067e64
Revises: 988223dcc93a
Create Date: 2024-10-24 20:22:53.626693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '584559067e64'
down_revision: Union[str, None] = '988223dcc93a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('journal_entry', schema=None) as batch_op:       
        batch_op.add_column(sa.Column('comment', sa.String(150), nullable=True))
   


def downgrade() -> None:
    with op.batch_alter_table('journal_entry', schema=None) as batch_op:       
        batch_op.drop_column('comment')
