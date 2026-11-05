from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.config import get_settings
from app.models import EmailOutbox, Inventory, OrderItem, ProductVariant
from app.services.inventory import release_stock
from app.services.orders import (
    OrderStateError,
    commit_order_sale,
    expire_order,
    expire_orders,
    reserve_order_stock,
)
from app.services.outbox import dispatch_pending
from app.services.reconciliation import reconcile, summary
from app.services.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    is_retryable_db_error,
    retry_with_backoff,
    run_with_db_retry,
)
from app.services.razorpay import (
    RazorpayError,
    RazorpayGateway,
    RazorpayTransientError,
    reset_circuit_breakers,
)

from .test_orders import (
    _add,
    _checkout,
    _inventory,
    _new_cart,
    _order,
    _order_with_one_pair,
    _payload,
)

from .factories import make_category, make_product, make_variant


def test_retry_with_backoff_uses_bounded_exponential_delays() -> None:
    delays: list[float] = []
    calls = {"count": 0}

    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("try again")
        return "ok"

    result = retry_with_backoff(
        flaky,
        attempts=3,
        base_delay=0.1,
        max_delay=1.0,
        sleep=delays.append,
    )
    assert result == "ok"
    assert delays == [0.1, 0.2]


def test_retry_with_backoff_gives_up_after_attempts() -> None:
    calls = {"count": 0}

    def always_fails() -> None:
        calls["count"] += 1
        raise RuntimeError("still broken")

    with pytest.raises(RuntimeError, match="still broken"):
        retry_with_backoff(always_fails, attempts=3, sleep=lambda _: None)
    assert calls["count"] == 3


def test_circuit_breaker_opens_and_half_opens() -> None:
    now = {"value": 0.0}
    breaker = CircuitBreaker(
        name="test",
        failure_threshold=2,
        recovery_seconds=10,
        clock=lambda: now["value"],
    )
    breaker.record_failure()
    assert not breaker.is_open
    breaker.record_failure()
    assert breaker.is_open
    with pytest.raises(CircuitOpenError):
        breaker.before_call()

    now["value"] = 10.0
    breaker.before_call()  # half-open trial is allowed
    breaker.record_success()
    assert not breaker.is_open


def test_retryable_database_errors_are_recognised() -> None:
    serialization = SimpleNamespace(pgcode="40001")
    deadlock = SimpleNamespace(sqlstate="40P01")
    other = SimpleNamespace(pgcode="23505")
    assert is_retryable_db_error(serialization)
    assert is_retryable_db_error(deadlock)
    assert not is_retryable_db_error(other)
    assert is_retryable_db_error(RuntimeError("deadlock detected"))


def test_run_with_db_retry_rolls_back_and_retries() -> None:
    calls = {"count": 0}
    rollbacks = {"count": 0}

    def fake_rollback() -> None:
        rollbacks["count"] += 1

    fake_db = SimpleNamespace(rollback=fake_rollback)

    def work() -> str:
        calls["count"] += 1
        if calls["count"] < 2:
            raise DBAPIError("stmt", {}, Exception("deadlock detected"))
        return "done"

    assert run_with_db_retry(fake_db, work, attempts=3, sleep=lambda _: None) == "done"
    assert calls["count"] == 2
    assert rollbacks["count"] == 1


def test_razorpay_transient_errors_are_retried_then_the_breaker_opens(
    monkeypatch,
) -> None:
    reset_circuit_breakers()
    settings = get_settings()
    gateway = RazorpayGateway(settings)
    calls = {"count": 0}

    def always_transient(*_args, **_kwargs):
        calls["count"] += 1
        raise RazorpayTransientError("503 from Razorpay")

    monkeypatch.setattr(gateway, "_post_once", always_transient)
    monkeypatch.setattr("app.services.resilience.time.sleep", lambda _: None)

    with pytest.raises(RazorpayTransientError):
        gateway._post("/orders", {})
    assert calls["count"] == 3

    # The breaker has already recorded three failures. A second call trips it
    # open instead of hammering Razorpay again.
    with pytest.raises(RazorpayError):
        gateway._post("/orders", {})
    reset_circuit_breakers()


def test_razorpay_call_passes_the_configured_timeout(monkeypatch) -> None:
    settings = get_settings()
    gateway = RazorpayGateway(settings)
    seen: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self) -> bytes:
            return b'{"id": "order_test"}'

    def fake_urlopen(request, timeout=None):  # noqa: ANN001 - test double
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("app.services.razorpay.urlrequest.urlopen", fake_urlopen)
    assert gateway._post_once("/orders", {}) == {"id": "order_test"}
    assert seen["timeout"] == settings.razorpay_timeout_seconds


def test_email_failure_never_undoes_a_captured_payment(
    client: TestClient, db_session, monkeypatch
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)

    def smtp_is_down(**_kwargs):
        raise OSError("connection refused by SMTP")

    monkeypatch.setattr("app.services.outbox.send_email", smtp_is_down)

    paid = client.post(f"/orders/{body['public_id']}/mock-pay")
    assert paid.status_code == 200, paid.text
    assert paid.json()["status"] == "paid"

    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    assert _inventory(db_session, "RELAY-UK7").on_hand == 9

    db_session.expire_all()
    row = db_session.scalar(select(EmailOutbox).where(EmailOutbox.order_id == order.id))
    assert row is not None
    assert row.status == "pending"
    assert row.attempts >= 1
    assert "connection refused" in (row.last_error or "")


def test_outbox_retries_and_marks_sent(
    client: TestClient, db_session, monkeypatch
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)

    monkeypatch.setattr(
        "app.services.outbox.send_email",
        lambda **_kwargs: (_ for _ in ()).throw(OSError("temporary")),
    )
    client.post(f"/orders/{body['public_id']}/mock-pay")

    db_session.expire_all()
    order = _order(db_session, body["public_id"])
    row = db_session.scalar(select(EmailOutbox).where(EmailOutbox.order_id == order.id))
    assert row is not None and row.status == "pending"

    monkeypatch.setattr("app.services.outbox.send_email", lambda **_kwargs: True)
    assert dispatch_pending(db_session, get_settings(), order_id=order.id) == 1

    db_session.expire_all()
    row = db_session.scalar(select(EmailOutbox).where(EmailOutbox.order_id == order.id))
    assert row is not None and row.status == "sent"
    assert row.sent_at is not None
    order = _order(db_session, body["public_id"])
    assert order.confirmation_email_sent_at is not None


def test_order_reservation_is_atomic_when_one_line_is_out_of_stock(
    client: TestClient, db_session
) -> None:
    first = make_product(
        db_session,
        make_category(db_session, slug="first-cat", code="FC"),
        id="ATOM-1",
        sku_prefix="ATOM-1",
        slug="atom-one",
        status="published",
    )
    second = make_product(
        db_session,
        make_category(db_session, slug="second-cat", code="SC"),
        id="ATOM-2",
        sku_prefix="ATOM-2",
        slug="atom-two",
        status="published",
    )
    make_variant(db_session, first, sku="ATOM-1-UK7", on_hand=5)
    make_variant(db_session, second, sku="ATOM-2-UK7", on_hand=5)

    _new_cart(client)
    _add(client, "ATOM-1-UK7", 1)
    _add(client, "ATOM-2-UK7", 1)
    body = _checkout(client, _payload())

    # Expire the order so both lines are released, then remove the second
    # line's stock. Re-reserving must fail as a unit.
    order = _order(db_session, body["public_id"])
    order.reservation_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()
    assert expire_orders(db_session) == 1

    second_inventory = _inventory(db_session, "ATOM-2-UK7")
    second_inventory.on_hand = 0
    db_session.commit()

    db_session.expire_all()
    order = _order(db_session, body["public_id"])
    with pytest.raises(Exception):
        reserve_order_stock(db_session, order)

    db_session.expire_all()
    assert _inventory(db_session, "ATOM-1-UK7").reserved == 0
    order = _order(db_session, body["public_id"])
    assert {item.stock_state for item in order.items} == {"released"}


def test_sale_is_atomic_when_a_later_line_lost_its_reservation(
    client: TestClient, db_session
) -> None:
    first = make_product(
        db_session,
        make_category(db_session, slug="sale-cat", code="SL"),
        id="SALE-1",
        sku_prefix="SALE-1",
        slug="sale-one",
        status="published",
    )
    second = make_product(
        db_session,
        make_category(db_session, slug="sale-two-cat", code="S2"),
        id="SALE-2",
        sku_prefix="SALE-2",
        slug="sale-two",
        status="published",
    )
    make_variant(db_session, first, sku="SALE-1-UK7", on_hand=5)
    make_variant(db_session, second, sku="SALE-2-UK7", on_hand=5)
    _new_cart(client)
    _add(client, "SALE-1-UK7", 1)
    _add(client, "SALE-2-UK7", 1)
    body = _checkout(client, _payload())

    db_session.expire_all()
    order = _order(db_session, body["public_id"])
    # Release the second line behind the order's back. The first line is still
    # reserved, so the sale must roll back as a unit rather than half-complete.
    item = next(line for line in order.items if line.sku == "SALE-2-UK7")
    release_stock(
        db_session,
        item.variant_id,
        item.quantity,
        reference=f"{item.reservation_reference}:test-release",
    )
    item.stock_state = "released"
    db_session.commit()

    with pytest.raises(OrderStateError):
        commit_order_sale(db_session, order)

    db_session.expire_all()
    inventory = _inventory(db_session, "SALE-1-UK7")
    assert inventory.on_hand == 5
    assert inventory.reserved == 1
    assert _inventory(db_session, "SALE-2-UK7").on_hand == 5


def test_reconciliation_passes_for_a_paid_order(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)
    assert client.post(f"/orders/{body['public_id']}/mock-pay").status_code == 200
    assert reconcile(db_session) == []


def test_reconciliation_reports_order_total_mismatch(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)
    order = _order(db_session, body["public_id"])
    order.total_paise += 100
    db_session.commit()

    problems = reconcile(db_session)
    assert any("total_paise" in problem for problem in problems)
    assert summary(problems)["ok"] is False


def test_reconciliation_reports_negative_inventory(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)
    inventory = _inventory(db_session, "RELAY-UK7")
    # The CHECK constraint normally makes this impossible. Reconciliation is the
    # second line of defence, so bypass the guard for this test only.
    if db_session.bind.dialect.name != "sqlite":
        pytest.skip("check-constraint bypass is SQLite-only")
    db_session.execute(text("PRAGMA ignore_check_constraints=ON"))
    inventory.on_hand = -1
    db_session.commit()
    db_session.execute(text("PRAGMA ignore_check_constraints=OFF"))

    problems = reconcile(db_session)
    assert any("negative" in problem for problem in problems)


def test_database_rejects_negative_inventory(db_session) -> None:
    from .factories import make_category, make_product, make_variant

    product = make_product(
        db_session,
        make_category(db_session, slug="neg-cat", code="NG"),
        id="NEG-1",
        sku_prefix="NEG-1",
        slug="neg-one",
        status="published",
    )
    variant = make_variant(db_session, product, sku="NEG-1-UK7", on_hand=1)
    inventory = _inventory(db_session, "NEG-1-UK7")
    inventory.on_hand = -1
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    assert _inventory(db_session, "NEG-1-UK7").on_hand == 1


def test_reconciliation_reports_flagged_payment_without_a_refund(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)
    order = _order(db_session, body["public_id"])
    payment = order.payments[-1]
    payment.needs_review = True
    payment.review_reason = "payment currency mismatch (USD vs INR)"
    payment.amount_paise = order.total_paise
    order.status = "refund_pending"
    db_session.commit()

    problems = reconcile(db_session)
    assert any("flagged for review" in problem for problem in problems)


def test_reconciliation_reports_paid_order_without_captured_payment(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)
    order = _order(db_session, body["public_id"])
    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    db_session.commit()

    problems = reconcile(db_session)
    assert any("no captured payment" in problem for problem in problems)


def test_expiry_sweeper_continues_when_one_order_cannot_release_stock(
    client: TestClient, db_session
) -> None:
    first = make_product(
        db_session,
        make_category(db_session, slug="sweep-a-cat", code="SA"),
        id="SWEEP-A",
        sku_prefix="SWEEP-A",
        slug="sweep-a",
        status="published",
    )
    second = make_product(
        db_session,
        make_category(db_session, slug="sweep-b-cat", code="SB"),
        id="SWEEP-B",
        sku_prefix="SWEEP-B",
        slug="sweep-b",
        status="published",
    )
    make_variant(db_session, first, sku="SWEEP-A-UK7", on_hand=5)
    make_variant(db_session, second, sku="SWEEP-B-UK7", on_hand=5)

    _new_cart(client)
    _add(client, "SWEEP-A-UK7", 1)
    body_a = _checkout(client)
    _new_cart(client)
    _add(client, "SWEEP-B-UK7", 1)
    body_b = _checkout(client)

    # Corrupt only the first order's reserved counter, as a lost or hand-edited
    # row would. Releasing it must fail without blocking the rest of the sweep.
    first_inventory = _inventory(db_session, "SWEEP-A-UK7")
    first_inventory.reserved = 0
    db_session.commit()

    expired_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    for public_id in (body_a["public_id"], body_b["public_id"]):
        _order(db_session, public_id).reservation_expires_at = expired_at
    db_session.commit()

    assert expire_orders(db_session) == 1

    db_session.expire_all()
    assert _order(db_session, body_b["public_id"]).status == "expired"
    assert _order(db_session, body_a["public_id"]).status == "awaiting_payment"


def test_expiry_sweeper_treats_naive_timestamps_as_utc(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)
    order = _order(db_session, body["public_id"])
    # A row written by an older tool may be naive. It is UTC by convention.
    order.reservation_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        minutes=1
    )
    db_session.commit()

    assert expire_order(db_session, order, now=datetime.now(timezone.utc)) is True
    db_session.expire_all()
    assert _order(db_session, body["public_id"]).status == "expired"
    assert expire_orders(db_session) == 0
