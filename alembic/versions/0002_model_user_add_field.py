"""model User add field

Revision ID: 0002
Revises: 0001
Create Date: 2025-03-29 18:33:22.742832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_staff', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_users_is_staff'), 'users', ['is_staff'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_is_staff'), table_name='users')
    op.drop_column('users', 'is_staff')
    # ### end Alembic commands ###
