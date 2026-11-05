from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..models import Inventory, InventoryEvent, ProductVariant


class InventoryError(Exception):
    pass


class InventoryNotFound(InventoryError):
    pass


class OutOfStock(InventoryError):
    pass


def get_inventory(db: Session, variant_id: int) -> Inventory:
    inventory = db.scalar(select(Inventory).where(Inventory.variant_id == variant_id))
    if inventory is None:
        raise InventoryNotFound(f"No inventory row for variant {variant_id}")
    return inventory


def get_inventory_by_sku(db: Session, sku: str) -> Inventory:
    variant = db.scalar(select(ProductVariant).where(ProductVariant.sku == sku))
    if variant is None:
        raise InventoryNotFound(f"No variant {sku}")
    return get_inventory(db, variant.id)


def _event(
    db: Session,
    variant_id: int,
    event_type: str,
    quantity_delta: int,
    reference: str | None,
    note: str | None,
) -> None:
    db.add(
        InventoryEvent(
            variant_id=variant_id,
            event_type=event_type,
            quantity_delta=quantity_delta,
            reference=reference,
            note=note,
        )
    )


def _existing_reference(db: Session, reference: str | None) -> bool:
    if not reference:
        return False
    return (
        db.scalar(select(InventoryEvent.id).where(InventoryEvent.reference == reference))
        is not None
    )


def reserve_stock(
    db: Session,
    variant_id: int,
    quantity: int,
    reference: str | None = None,
    note: str | None = None,
    *,
    commit: bool = True,
) -> Inventory:
    """Atomically reserve available units.

    The conditional UPDATE is the oversell guard. It is safe under concurrent
    requests because the database decides the winner, not the application.

    ``commit=False`` lets an order-level operation group several lines into one
    transaction, so a crash mid-order cannot sell half a pair set.
    """

    if quantity <= 0:
        raise ValueError("quantity must be positive")

    if _existing_reference(db, reference):
        return get_inventory(db, variant_id)

    result = db.execute(
        update(Inventory)
        .where(
            Inventory.variant_id == variant_id,
            Inventory.on_hand - Inventory.reserved >= quantity,
        )
        .values(
            reserved=Inventory.reserved + quantity,
            version=Inventory.version + 1,
        )
    )
    if result.rowcount != 1:
        if commit:
            db.rollback()
        if db.scalar(select(Inventory.id).where(Inventory.variant_id == variant_id)) is None:
            raise InventoryNotFound(f"No inventory row for variant {variant_id}")
        raise OutOfStock(f"Variant {variant_id} does not have {quantity} available")

    _event(db, variant_id, "reservation", -quantity, reference, note)
    if commit:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
    else:
        db.flush()
    return get_inventory(db, variant_id)


def release_stock(
    db: Session,
    variant_id: int,
    quantity: int,
    reference: str | None = None,
    note: str | None = None,
    *,
    commit: bool = True,
) -> Inventory:
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    if _existing_reference(db, reference):
        return get_inventory(db, variant_id)

    result = db.execute(
        update(Inventory)
        .where(
            Inventory.variant_id == variant_id,
            Inventory.reserved >= quantity,
        )
        .values(
            reserved=Inventory.reserved - quantity,
            version=Inventory.version + 1,
        )
    )
    if result.rowcount != 1:
        if commit:
            db.rollback()
        raise OutOfStock(f"Variant {variant_id} does not have {quantity} reserved")

    _event(db, variant_id, "release", quantity, reference, note)
    if commit:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
    else:
        db.flush()
    return get_inventory(db, variant_id)


def commit_sale(
    db: Session,
    variant_id: int,
    quantity: int,
    reference: str | None = None,
    note: str | None = None,
    *,
    commit: bool = True,
) -> Inventory:
    """Convert a reservation into a sale."""

    if quantity <= 0:
        raise ValueError("quantity must be positive")

    if _existing_reference(db, reference):
        return get_inventory(db, variant_id)

    result = db.execute(
        update(Inventory)
        .where(
            Inventory.variant_id == variant_id,
            Inventory.reserved >= quantity,
            Inventory.on_hand >= quantity,
        )
        .values(
            on_hand=Inventory.on_hand - quantity,
            reserved=Inventory.reserved - quantity,
            version=Inventory.version + 1,
        )
    )
    if result.rowcount != 1:
        if commit:
            db.rollback()
        raise OutOfStock(f"Variant {variant_id} cannot complete {quantity} sale")

    _event(db, variant_id, "sale", -quantity, reference, note)
    if commit:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
    else:
        db.flush()
    return get_inventory(db, variant_id)


def adjust_stock(
    db: Session,
    variant_id: int,
    quantity_delta: int,
    reference: str | None = None,
    note: str | None = None,
    *,
    commit: bool = True,
) -> Inventory:
    if quantity_delta == 0:
        raise ValueError("quantity_delta must not be zero")

    if _existing_reference(db, reference):
        return get_inventory(db, variant_id)

    result = db.execute(
        update(Inventory)
        .where(
            Inventory.variant_id == variant_id,
            Inventory.on_hand + quantity_delta >= Inventory.reserved,
            Inventory.on_hand + quantity_delta >= 0,
        )
        .values(
            on_hand=Inventory.on_hand + quantity_delta,
            version=Inventory.version + 1,
        )
    )
    if result.rowcount != 1:
        if commit:
            db.rollback()
        if db.scalar(select(Inventory.id).where(Inventory.variant_id == variant_id)) is None:
            raise InventoryNotFound(f"No inventory row for variant {variant_id}")
        raise OutOfStock(f"Adjustment would make variant {variant_id} negative or below reserved")

    _event(db, variant_id, "adjustment", quantity_delta, reference, note)
    if commit:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
    else:
        db.flush()
    return get_inventory(db, variant_id)


def list_events(db: Session, variant_id: int) -> list[InventoryEvent]:
    return list(
        db.scalars(
            select(InventoryEvent)
            .where(InventoryEvent.variant_id == variant_id)
            .order_by(InventoryEvent.id)
        ).all()
    )
