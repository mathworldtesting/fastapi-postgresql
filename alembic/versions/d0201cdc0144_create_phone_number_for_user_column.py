"""Create phone number for user column

Revision ID: d0201cdc0144
Revises: 
Create Date: 2024-10-01 17:59:31.545141
# run code: alembic upgrade <Revision ID>
# run code: alembic downgrade -1 # downgrade the last revision

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0201cdc0144'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
