# Runbook: backup and restore

The scripts are intentionally small wrappers around `pg_dump`/`pg_restore` for
PostgreSQL and a file copy for SQLite. They never print the database URL.

## What is covered

- `apps/api/scripts/backup_db.sh` writes a custom-format PostgreSQL dump
  (`backups/santvana-<UTC>.dump`) or a SQLite file copy.
- `apps/api/scripts/restore_db.sh` restores a dump. **PostgreSQL restore is
  destructive:** it runs `pg_restore --clean --if-exists` against the target.
- `apps/api/app/services/backup.py` contains the logic both scripts and
  `tests/test_backup_restore.py` use.

## Take a backup

```bash
cd apps/api
DATABASE_URL='postgresql+psycopg://user:pass@host:5432/santvana' \
BACKUP_DIR=/var/backups/santvana \
./scripts/backup_db.sh
```

Or from the repo root: `make backup` (uses the current environment).

Verify the file exists and is non-trivial in size. Store it off the database
host. This repository does **not** automate retention, encryption at rest or
off-site copies; that is an operations task.

## Restore drill (do this before you need it)

1. Create a scratch database. Never practise on the live database.
2. Point `DATABASE_URL` at the scratch database.
3. Restore.
4. Run migrations to head and `make reconcile`.

```bash
createdb -h localhost -U santvana santvana_restore_check

cd apps/api
DATABASE_URL='postgresql+psycopg://santvana:santvana@localhost:5432/santvana_restore_check' \
./scripts/restore_db.sh backups/santvana-20261104T000000Z.dump

DATABASE_URL='postgresql+psycopg://santvana:santvana@localhost:5432/santvana_restore_check' \
alembic upgrade head

DATABASE_URL='postgresql+psycopg://santvana:santvana@localhost:5432/santvana_restore_check' \
python scripts/reconcile.py

dropdb -h localhost -U santvana santvana_restore_check
```

The automated test `tests/test_backup_restore.py` does a SQLite round-trip
locally and a PostgreSQL scratch-database restore in CI when `pg_dump` and
`pg_restore` are available.

## Restore into production (incident)

This is a destructive, high-risk action. Get a second person to read the command
back.

1. Stop application writes (scale the API down or put it in maintenance).
2. Take a fresh backup of the current database first, even if it is damaged.
3. Confirm the dump timestamp and checksum.
4. Restore into the target database.
5. Run `alembic upgrade head`.
6. Start the API, check `/health/ready`, then `make reconcile`.
7. Replay any webhooks Razorpay retried while the API was down. Check
   `webhook_events` for `failed`/`received` rows.
8. Re-drive the outbox (`make outbox`) so confirmation emails are attempted.
9. Record what was restored, from which dump, by whom, and what data was lost.

## SQLite (development only)

```bash
cd apps/api
DATABASE_URL='sqlite:///./santvana-dev.db' ./scripts/backup_db.sh
DATABASE_URL='sqlite:///./santvana-restored.db' ./scripts/restore_db.sh backups/santvana-<stamp>.sqlite
```

SQLite backups are a file copy. Do not treat this as a production backup plan.

## Failure modes

- `pg_dump`/`pg_restore` missing → the script raises `BackupError`. Install the
  PostgreSQL client tools.
- Backup file missing → restore refuses rather than creating an empty database.
- Restore fails midway → the target is in an unknown state. Restore again from
  the dump; do not start the API against a partial restore.
