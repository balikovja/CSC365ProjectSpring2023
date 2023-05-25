"""Unique username

Revision ID: 7d80eb0137ee
Revises: 223ef9cbabbe
Create Date: 2023-05-24 22:10:41.260032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d80eb0137ee'
down_revision = '223ef9cbabbe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_username", "users", ["username"])


def downgrade() -> None:
    op.drop_constraint("uq_username", "users")
