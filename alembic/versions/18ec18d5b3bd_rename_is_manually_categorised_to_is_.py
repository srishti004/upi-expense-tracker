"""rename is_manually_categorised to is_manually_categorized

Revision ID: 18ec18d5b3bd
Revises: 2c6ce3197061
Create Date: 2026-06-15 22:37:04.013522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18ec18d5b3bd'
down_revision: Union[str, Sequence[str], None] = '2c6ce3197061'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('transactions', 'is_manually_categorised', new_column_name='is_manually_categorized')

def downgrade():
    op.alter_column('transactions', 'is_manually_categorized', new_column_name='is_manually_categorised')