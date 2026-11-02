"""guest carts, reservations and full-text search

Revision ID: c4a1f2d3e5b6
Revises: b137d92f11bf
Create Date: 2026-11-02 10:00:00.000000

Adds the guest cart and time-boxed reservation tables for Milestone 2, plus a
PostgreSQL-only GIN index for the catalogue search document. SQLite (the local
and test database) keeps the fallback substring search and gets no index.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4a1f2d3e5b6'
down_revision: Union[str, None] = 'b137d92f11bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEARCH_DOCUMENT = (
    "to_tsvector('english', "
    "coalesce(name, '') || ' ' || "
    "coalesce(sub_category, '') || ' ' || "
    "coalesce(colour, '') || ' ' || "
    "coalesce(short_description, '') || ' ' || "
    "coalesce(long_description, ''))"
)


def upgrade() -> None:
    op.create_table(
        'carts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('carts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_carts_token'), ['token'], unique=True)

    op.create_table(
        'cart_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('variant_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('reservation_reference', sa.String(length=120), nullable=False),
        sa.Column('reservation_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.CheckConstraint('quantity > 0', name='ck_cart_items_quantity_positive'),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['variant_id'], ['product_variants.id'], ondelete='RESTRICT'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cart_id', 'variant_id', name='uq_cart_items_variant'),
        sa.UniqueConstraint('reservation_reference'),
    )
    with op.batch_alter_table('cart_items', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_cart_items_cart_id'), ['cart_id'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_cart_items_variant_id'), ['variant_id'], unique=False
        )

    if op.get_bind().dialect.name == 'postgresql':
        op.execute(
            'CREATE INDEX ix_products_search_tsv ON products '
            f'USING gin ({SEARCH_DOCUMENT})'
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('DROP INDEX IF EXISTS ix_products_search_tsv')

    with op.batch_alter_table('cart_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cart_items_variant_id'))
        batch_op.drop_index(batch_op.f('ix_cart_items_cart_id'))

    op.drop_table('cart_items')
    with op.batch_alter_table('carts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_carts_token'))

    op.drop_table('carts')
