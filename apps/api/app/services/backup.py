"""PostgreSQL backup and restore helpers.

The shell scripts in ``scripts/`` call these functions so the restore test can
exercise exactly the same commands an operator runs.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class BackupError(RuntimeError):
    pass


def pg_tool_url(database_url: str) -> str:
    """Strip SQLAlchemy driver suffixes that libpq tools do not understand."""

    return (
        database_url.replace("postgresql+psycopg://", "postgresql://")
        .replace("postgresql+psycopg2://", "postgresql://")
        .replace("postgres://", "postgresql://")
    )


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if path is None:
        raise BackupError(f"{tool} is not installed or not on PATH")
    return path


def is_sqlite(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def sqlite_path(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        return Path(database_url.removeprefix("sqlite:///"))
    if database_url.startswith("sqlite://"):
        return Path(database_url.removeprefix("sqlite://"))
    raise BackupError(f"Unsupported SQLite URL: {database_url}")


def dump_database(database_url: str, output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if is_sqlite(database_url):
        source = sqlite_path(database_url)
        if not source.exists():
            raise BackupError(f"SQLite database does not exist: {source}")
        shutil.copy2(source, output)
        return output

    pg_dump = _require("pg_dump")
    subprocess.run(
        [
            pg_dump,
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(output),
            pg_tool_url(database_url),
        ],
        check=True,
    )
    return output


def restore_database(database_url: str, dump: str | Path) -> None:
    dump = Path(dump)
    if not dump.exists():
        raise BackupError(f"Backup file does not exist: {dump}")
    if is_sqlite(database_url):
        target = sqlite_path(database_url)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dump, target)
        return

    pg_restore = _require("pg_restore")
    subprocess.run(
        [
            pg_restore,
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            "--dbname",
            pg_tool_url(database_url),
            str(dump),
        ],
        check=True,
    )
