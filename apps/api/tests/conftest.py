from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# The suite runs against SQLite by default (fast local fallback) and against
# PostgreSQL in CI when TEST_DATABASE_URL is set. See POSTGRES-VS-SQLITE.md.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "").strip() or None

os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL or "sqlite:///:memory:")
os.environ.setdefault("ADMIN_API_TOKEN", "test-admin-token")
os.environ.setdefault("OTEL_ENABLED", "false")
os.environ.setdefault("MAIL_ENABLED", "false")
os.environ.setdefault("RAZORPAY_KEY_ID", "")
os.environ.setdefault("RAZORPAY_KEY_SECRET", "")
os.environ.setdefault("RAZORPAY_WEBHOOK_SECRET", "test-webhook-secret")
os.environ.setdefault("RAZORPAY_MOCK", "true")
os.environ.setdefault("APP_ENV", "development")

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


def _sqlite_engine(tmp_path) -> Engine:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )

    @event.listens_for(engine, "connect")
    def _pragmas(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

    return engine


@pytest.fixture()
def db_engine(tmp_path):
    if TEST_DATABASE_URL:
        engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        try:
            yield engine
        finally:
            Base.metadata.drop_all(engine)
            engine.dispose()
        return

    engine = _sqlite_engine(tmp_path)
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    with session_factory() as session:
        yield session


@pytest.fixture()
def client(db_engine) -> Generator[TestClient, None, None]:
    session_factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
