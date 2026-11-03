"""orders, payments and Razorpay webhook events

Revision ID: e6c3f9a2b8d1
Revises: d5b2e8f1a3c7
Create Date: 2026-11-03 11:00:00.000000

All money is stored as integer paise. Order lines snapshot the product name,
SKU, size and price so a later catalogue edit cannot change a placed order.
Webhook events have a unique provider event id for replay safety.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6c3f9a2b8d1"
down_revision: Union[str, None] = "d5b2e8f1a3c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("public_id", sa.String(length=48), nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("customer_name", sa.String(length=120), nullable=False),
        sa.Column("customer_email", sa.String(length=254), nullable=False),
        sa.Column("customer_phone", sa.String(length=16), nullable=False),
        sa.Column("address_line1", sa.String(length=200), nullable=False),
        sa.Column("address_line2", sa.String(length=200), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=False),
        sa.Column("pincode", sa.String(length=6), nullable=False),
        sa.Column("country", sa.String(length=60), nullable=False),
        sa.Column("seller_state", sa.String(length=120), nullable=False),
        sa.Column("seller_gstin", sa.String(length=120), nullable=False),
        sa.Column("subtotal_paise", sa.Integer(), nullable=False),
        sa.Column("gst_paise", sa.Integer(), nullable=False),
        sa.Column("shipping_paise", sa.Integer(), nullable=False),
        sa.Column("total_paise", sa.Integer(), nullable=False),
        sa.Column("reservation_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmation_email_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.CheckConstraint("total_paise >= 0", name="ck_orders_total_non_negative"),
        sa.CheckConstraint("gst_paise >= 0", name="ck_orders_gst_non_negative"),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cart_id", name="uq_orders_cart"),
        sa.UniqueConstraint("public_id", name="uq_orders_public_id"),
    )
    op.create_index("ix_orders_status", "orders", ["status"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("variant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.String(length=60), nullable=True),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("product_slug", sa.String(length=200), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("size_uk", sa.String(length=12), nullable=False),
        sa.Column("hsn", sa.String(length=20), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_paise", sa.Integer(), nullable=False),
        sa.Column("line_total_paise", sa.Integer(), nullable=False),
        sa.Column("taxable_value_paise", sa.Integer(), nullable=False),
        sa.Column("gst_paise", sa.Integer(), nullable=False),
        sa.Column("gst_rate_pct", sa.Integer(), nullable=False),
        sa.Column("reservation_reference", sa.String(length=160), nullable=False),
        sa.Column("stock_state", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        sa.CheckConstraint(
            "line_total_paise >= 0", name="ck_order_items_total_non_negative"
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["variant_id"], ["product_variants.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "reservation_reference", name="uq_order_items_reservation_reference"
        ),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"], unique=False)
    op.create_index(
        "ix_order_items_variant_id", "order_items", ["variant_id"], unique=False
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_order_id", sa.String(length=80), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("amount_paise", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("method", sa.String(length=40), nullable=True),
        sa.Column("raw_status", sa.String(length=40), nullable=True),
        sa.Column("failure_code", sa.String(length=80), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("refund_id", sa.String(length=80), nullable=True),
        sa.Column("refunded_paise", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.CheckConstraint("amount_paise >= 0", name="ck_payments_amount_non_negative"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider_order_id", name="uq_payments_provider_order"
        ),
        sa.UniqueConstraint(
            "provider_payment_id", name="uq_payments_provider_payment"
        ),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"], unique=False)
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("event_id", sa.String(length=120), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", name="uq_webhook_events_event_id"),
    )
    op.create_index(
        "ix_webhook_events_status", "webhook_events", ["status"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_webhook_events_status", table_name="webhook_events")
    op.drop_table("webhook_events")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_order_items_variant_id", table_name="order_items")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_table("orders")
