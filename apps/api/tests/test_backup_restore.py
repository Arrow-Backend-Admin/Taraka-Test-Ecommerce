from __future__ import annotations

import os
import shutil
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.services.backup import (
    BackupError,
    dump_database,
    restore_database,
    sqlite_path,
)

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "").strip()
IS_POSTGRES = TEST_DATABASE_URL.startswith(("postgresql://", "postgresql+"))
HAS_PG_TOOLS = bool(shutil.which("pg_dump") and shutil.which("pg_restore"))


def test_sqlite_backup_round_trip(tmp_path) -> None:
    source = tmp_path / "source.db"
    source_engine = create_engine(f"sqlite:///{source}")
    with source_engine.begin() as connection:
        connection.execute(text("CREATE TABLE probe (id INTEGER PRIMARY KEY, note TEXT)"))
        connection.execute(text("INSERT INTO probe (id, note) VALUES (1, 'kept')"))
    source_engine.dispose()

    dump = dump_database(f"sqlite:///{source}", tmp_path / "backup.sqlite")
    assert dump.exists()

    target = tmp_path / "restored.db"
    restore_database(f"sqlite:///{target}", dump)
    assert sqlite_path(f"sqlite:///{target}") == target

    target_engine = create_engine(f"sqlite:///{target}")
    with target_engine.connect() as connection:
        assert connection.scalar(text("SELECT note FROM probe WHERE id = 1")) == "kept"
    target_engine.dispose()


def test_restore_refuses_a_missing_backup(tmp_path) -> None:
    with pytest.raises(BackupError):
        restore_database("sqlite:///unused.db", tmp_path / "missing.dump")


@pytest.mark.skipif(not IS_POSTGRES, reason="TEST_DATABASE_URL is not PostgreSQL")
@pytest.mark.skipif(not HAS_PG_TOOLS, reason="pg_dump/pg_restore are not installed")
def test_postgres_backup_restores_into_a_scratch_database(
    db_session, tmp_path
) -> None:
    url = make_url(TEST_DATABASE_URL)
    admin_url = url.set(database="postgres")
    scratch_name = f"santvana_restore_{uuid.uuid4().hex[:8]}"
    scratch_url = url.set(database=scratch_name)

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{scratch_name}"'))

    try:
        db_session.execute(
            text(
                "CREATE TABLE IF NOT EXISTS restore_probe "
                "(id INTEGER PRIMARY KEY, note TEXT NOT NULL)"
            )
        )
        db_session.execute(text("DELETE FROM restore_probe"))
        db_session.execute(
            text("INSERT INTO restore_probe (id, note) VALUES (1, 'kept')")
        )
        db_session.commit()

        dump = dump_database(
            TEST_DATABASE_URL, tmp_path / "postgres-backup.dump"
        )
        restore_database(
            scratch_url.render_as_string(hide_password=False), dump
        )

        scratch_engine = create_engine(scratch_url)
        try:
            with scratch_engine.connect() as connection:
                assert (
                    connection.scalar(
                        text("SELECT note FROM restore_probe WHERE id = 1")
                    )
                    == "kept"
                )
        finally:
            scratch_engine.dispose()
    finally:
        db_session.execute(text("DROP TABLE IF EXISTS restore_probe"))
        db_session.commit()
        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :name"
                ),
                {"name": scratch_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{scratch_name}"'))
        admin_engine.dispose()
