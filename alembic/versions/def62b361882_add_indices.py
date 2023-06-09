"""add_indices

Revision ID: def62b361882
Revises: 7d80eb0137ee
Create Date: 2023-06-07 14:53:24.951894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'def62b361882'
down_revision = '7d80eb0137ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    sql = sa.text(
        """
        CREATE INDEX idx_budgets_user_id ON budgets (user_id);
        CREATE INDEX idx_tags_user_id ON tags (user_id);
        CREATE INDEX idx_transactions_user_id ON transactions (user_id);
        """
    )
    op.execute(sql)


def downgrade() -> None:
    sql = sa.text(
        """
        DROP INDEX IF EXISTS idx_budgets_user_id;
        DROP INDEX IF EXISTS idx_tags_user_id;
        DROP INDEX IF EXISTS idx_transactions_user_id;
        """
    )
    op.execute(sql)
