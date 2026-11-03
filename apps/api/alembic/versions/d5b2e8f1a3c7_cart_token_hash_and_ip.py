"""cart token hash and per-IP reservation caps

Revision ID: d5b2e8f1a3c7
Revises: c4a1f2d3e5b6
Create Date: 2026-11-03 09:00:00.000000

Guest cart tokens move out of JSON/localStorage and into an httpOnly cookie.
Only the SHA-256 hash is stored, so a database leak cannot replay a cart. The
IP is stored as a salted hash and is used to cap how much stock one client can
hold.

Existing carts are backfilled by hashing the plaintext token that was already
in the database. Those carts keep working for a client that still sends the
legacy ``X-Cart-Token`` header; new clients use the cookie.

SQLite cannot ``ALTER COLUMN ... SET NOT NULL``, so the changes go through
Alembic batch operations. PostgreSQL uses the same statements directly.
"""
from typing import Sequence, Union

import hashlib

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5b2e8f1a3c7"
down_revision: Union[str, None] = "c4a1f2d3e5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("carts") as batch_op:
        batch_op.add_column(sa.Column("token_hash", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("ip_hash", sa.String(length=64), nullable=True))

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, token FROM carts")).fetchall()
    for cart_id, token in rows:
        token_hash = hashlib.sha256(str(token).encode("utf-8")).hexdigest()
        connection.execute(
            sa.text("UPDATE carts SET token_hash = :token_hash WHERE id = :cart_id"),
            {"token_hash": token_hash, "cart_id": cart_id},
        )

    with op.batch_alter_table("carts") as batch_op:
        batch_op.alter_column(
            "token_hash", existing_type=sa.String(length=64), nullable=False
        )
        batch_op.drop_index("ix_carts_token")
        batch_op.drop_column("token")
        batch_op.create_index("ix_carts_token_hash", ["token_hash"], unique=True)
        batch_op.create_index("ix_carts_ip_hash", ["ip_hash"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("carts") as batch_op:
        batch_op.add_column(sa.Column("token", sa.String(length=64), nullable=True))

    connection = op.get_bind()
    connection.execute(sa.text("UPDATE carts SET token = token_hash"))

    with op.batch_alter_table("carts") as batch_op:
        batch_op.alter_column(
            "token", existing_type=sa.String(length=64), nullable=False
        )
        batch_op.drop_index("ix_carts_ip_hash")
        batch_op.drop_index("ix_carts_token_hash")
        batch_op.drop_column("token_hash")
        batch_op.drop_column("ip_hash")
        batch_op.create_index("ix_carts_token", ["token"], unique=True)
