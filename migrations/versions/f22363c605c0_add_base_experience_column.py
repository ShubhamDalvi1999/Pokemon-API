"""add base_experience column

Revision ID: f22363c605c0
Revises: 
Create Date: 2024-02-04 19:11:23.697894

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f22363c605c0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add base_experience column
    op.add_column('pokemon', sa.Column('base_experience', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove base_experience column
    op.drop_column('pokemon', 'base_experience')
