"""Bounded retries and a small circuit breaker for outbound and database work.

These helpers are deliberately simple. They do not make a failing dependency
healthy; they stop a slow or broken dependency from consuming every worker and
they make the retry policy explicit and testable.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

T = TypeVar("T")


class CircuitOpenError(RuntimeError):
    """Raised when a dependency is failing and the breaker is open."""


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_seconds: float = 30.0
    clock: Callable[[], float] = time.monotonic
    _failures: int = 0
    _opened_at: float | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def before_call(self) -> None:
        with self._lock:
            if self._opened_at is None:
                return
            if self.clock() - self._opened_at >= self.recovery_seconds:
                # Half-open: let one trial through. A failure re-opens it.
                self._opened_at = None
                self._failures = self.failure_threshold - 1
                return
            raise CircuitOpenError(f"{self.name} circuit is open")

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._opened_at = None

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._opened_at = self.clock()

    @property
    def is_open(self) -> bool:
        with self._lock:
            if self._opened_at is None:
                return False
            return self.clock() - self._opened_at < self.recovery_seconds


def retry_with_backoff(
    func: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    retry_on: type[BaseException] | tuple[type[BaseException], ...] = Exception,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    last: BaseException | None = None
    for attempt in range(attempts):
        try:
            return func()
        except retry_on as exc:  # noqa: PERF203 - retry boundary is explicit
            last = exc
            if attempt == attempts - 1:
                raise
            sleep(min(max_delay, base_delay * (2**attempt)))
    raise RuntimeError("retry loop exited without a result") from last


RETRYABLE_PG_CODES = {"40001", "40P01", "55P03"}


def is_retryable_db_error(exc: BaseException) -> bool:
    """PostgreSQL serialization failure, deadlock or lock timeout."""

    original = getattr(exc, "orig", None) or exc
    code = getattr(original, "pgcode", None) or getattr(original, "sqlstate", None)
    if code in RETRYABLE_PG_CODES:
        return True
    message = str(original).lower()
    return any(
        marker in message
        for marker in ("deadlock detected", "could not serialize", "lock timeout")
    )


def run_with_db_retry(
    db: Session,
    func: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 0.05,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Run a unit of work, retrying only known-safe PostgreSQL conflicts.

    The caller must pass a function whose effects are safe to repeat. Payment
    and stock handlers are idempotent through their unique references and row
    locks, so a retry after a deadlock cannot double-sell.
    """

    for attempt in range(attempts):
        try:
            return func()
        except DBAPIError as exc:
            db.rollback()
            if attempt == attempts - 1 or not is_retryable_db_error(exc):
                raise
            sleep(base_delay * (2**attempt))
    raise RuntimeError("database retry loop exited without a result")
