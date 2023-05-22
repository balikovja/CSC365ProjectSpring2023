"""Initial version

Revision ID: 223ef9cbabbe
Revises: 
Create Date: 2023-05-20 11:56:01.234038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '223ef9cbabbe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with open("schema_creation.sql", "r") as file:
        sql = file.read()
    op.execute(sa.text(sql))


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("tags")
    op.drop_table("budgets")
    op.drop_table("users")
    op.drop_table("period_types")
    op.drop_table("categories")
