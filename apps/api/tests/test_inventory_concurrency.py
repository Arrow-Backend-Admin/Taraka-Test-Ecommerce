from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.models import Inventory, InventoryEvent
from app.services.inventory import OutOfStock, reserve_stock

from .factories import make_category, make_product, make_variant


def test_parallel_checkout_last_unit_only_one_wins(db_engine, db_session) -> None:
    category = make_category(db_session)
    product = make_product(db_session, category)
    variant = make_variant(db_session, product, on_hand=1)

    barrier = threading.Barrier(2)
    session_factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    def attempt(index: int) -> str:
        with session_factory() as session:
            barrier.wait(timeout=10)
            try:
                reserve_stock(
                    session,
                    variant.id,
                    1,
                    reference=f"parallel-reserve-{index}",
                )
                return "reserved"
            except OutOfStock:
                return "out_of_stock"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))

    assert sorted(results) == ["out_of_stock", "reserved"]

    db_session.expire_all()
    inventory = db_session.scalar(
        select(Inventory).where(Inventory.variant_id == variant.id)
    )
    assert inventory is not None
    assert inventory.on_hand == 1
    assert inventory.reserved == 1

    events = db_session.scalars(
        select(InventoryEvent).where(InventoryEvent.variant_id == variant.id)
    ).all()
    reservations = [event for event in events if event.event_type == "reservation"]
    assert len(reservations) == 1
    assert reservations[0].quantity_delta == -1
