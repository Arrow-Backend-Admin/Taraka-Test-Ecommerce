"""hardening: payment review flags, email outbox and integrity checks

Revision ID: f7d4a1c9e2b3
Revises: e6c3f9a2b8d1
Create Date: 2026-11-04 10:00:00.000000

Adds the durable email outbox and the database-level guards that the Phase 4
hardening gate requires. Existing rows are not rewritten; a production
deployment must reconcile before applying the CHECK constraints if it has
legacy data that violates them.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7d4a1c9e2b3"
down_revision: Union[str, None] = "e6c3f9a2b8d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("payments") as batch:
        batch.add_column(
            sa.Column(
                "needs_review",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch.add_column(sa.Column("review_reason", sa.Text(), nullable=True))
    op.create_index(
        "ix_payments_needs_review", "payments", ["needs_review"], unique=False
    )

    op.create_table(
        "email_outbox",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("to_email", sa.String(length=254), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "attempts >= 0", name="ck_email_outbox_attempts_non_negative"
        ),
        sa.CheckConstraint(
            "status in ('pending', 'sent', 'failed')",
            name="ck_email_outbox_status",
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", name="uq_email_outbox_order"),
    )
    op.create_index(
        "ix_email_outbox_order_id", "email_outbox", ["order_id"], unique=False
    )
    op.create_index(
        "ix_email_outbox_status", "email_outbox", ["status"], unique=False
    )

    with op.batch_alter_table("order_items") as batch:
        batch.create_check_constraint(
            "ck_order_items_unit_price_non_negative", "unit_price_paise >= 0"
        )
        batch.create_check_constraint(
            "ck_order_items_taxable_non_negative", "taxable_value_paise >= 0"
        )
        batch.create_check_constraint(
            "ck_order_items_gst_non_negative", "gst_paise >= 0"
        )
        batch.create_check_constraint(
            "ck_order_items_split_adds_up",
            "taxable_value_paise + gst_paise = line_total_paise",
        )
        batch.create_check_constraint(
            "ck_order_items_known_gst_rate", "gst_rate_pct in (5, 18)"
        )
        batch.create_check_constraint(
            "ck_order_items_stock_state",
            "stock_state in ('reserved', 'sold', 'released')",
        )

    with op.batch_alter_table("payments") as batch:
        batch.create_check_constraint(
            "ck_payments_refunded_non_negative", "refunded_paise >= 0"
        )


def downgrade() -> None:
    with op.batch_alter_table("payments") as batch:
        batch.drop_constraint("ck_payments_refunded_non_negative", type_="check")

    with op.batch_alter_table("order_items") as batch:
        batch.drop_constraint("ck_order_items_stock_state", type_="check")
        batch.drop_constraint("ck_order_items_known_gst_rate", type_="check")
        batch.drop_constraint("ck_order_items_split_adds_up", type_="check")
        batch.drop_constraint("ck_order_items_gst_non_negative", type_="check")
        batch.drop_constraint("ck_order_items_taxable_non_negative", type_="check")
        batch.drop_constraint(
            "ck_order_items_unit_price_non_negative", type_="check"
        )

    op.drop_index("ix_email_outbox_status", table_name="email_outbox")
    op.drop_index("ix_email_outbox_order_id", table_name="email_outbox")
    op.drop_table("email_outbox")

    op.drop_index("ix_payments_needs_review", table_name="payments")
    with op.batch_alter_table("payments") as batch:
        batch.drop_column("review_reason")
        batch.drop_column("needs_review")
