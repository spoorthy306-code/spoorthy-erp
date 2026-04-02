"""Add nature column to ledgers table.

Revision ID: 001_add_ledger_nature
Revises:
Create Date: 2026-04-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "001_add_ledger_nature"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add nature column and index to ledgers table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("ledgers")}

    if "nature" not in columns:
        op.add_column(
            "ledgers",
            sa.Column("nature", sa.String(length=50), nullable=False, server_default="Debit"),
        )

    indexes = {ix["name"] for ix in inspector.get_indexes("ledgers")}
    if "ix_ledgers_nature" not in indexes:
        op.create_index("ix_ledgers_nature", "ledgers", ["nature"], unique=False)

    op.execute(
        """
        UPDATE ledgers
        SET nature = CASE
            WHEN COALESCE(debit_amount, 0) > 0 THEN 'Debit'
            WHEN COALESCE(credit_amount, 0) > 0 THEN 'Credit'
            ELSE 'Debit'
        END
        """
    )


def downgrade() -> None:
    """Remove nature index/column from ledgers table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    indexes = {ix["name"] for ix in inspector.get_indexes("ledgers")}
    if "ix_ledgers_nature" in indexes:
        op.drop_index("ix_ledgers_nature", table_name="ledgers")

    columns = {c["name"] for c in inspector.get_columns("ledgers")}
    if "nature" in columns:
        op.drop_column("ledgers", "nature")
