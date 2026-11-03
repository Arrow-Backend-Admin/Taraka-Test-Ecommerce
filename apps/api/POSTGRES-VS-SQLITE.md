# PostgreSQL vs SQLite

PostgreSQL 16 is the production target and the database the CI suite runs
against. SQLite is the fast local fallback so the API can start without Docker.
The application code is dialect-aware in exactly two places: catalogue search
and Alembic DDL. Everything else uses portable SQLAlchemy constructs.

Run the suite against PostgreSQL:

```bash
export TEST_DATABASE_URL="postgresql+psycopg://santvana:santvana@localhost:5432/santvana_test"
pytest
```

Without `TEST_DATABASE_URL` the same tests run against a temporary SQLite file.

## Behaviour differences

### Full-text search

| | PostgreSQL | SQLite |
| --- | --- | --- |
| Match | `to_tsvector('english', …) @@ plainto_tsquery('english', …)` | `ILIKE '%query%'` on the same five fields |
| Stemming | Yes (`running` matches `run`) | No |
| Stop words | Removed by the `english` configuration | Not removed |
| Ranking | `ts_rank` descending, then name | Name only |
| Index | GIN index `ix_products_search_tsv` | None (table scan) |
| Phrase/prefix | `plainto_tsquery` ANDs the terms | Substring, so `rel` matches `relay` |
| Punctuation | Tokenised away | Matched literally |

Practical effect: a search for `running` finds running shoes on both. A search
for `run` finds them only on PostgreSQL. A search for a partial word finds more
on SQLite than on PostgreSQL. Search tests assert only behaviour that holds on
both dialects; the PostgreSQL-only stemming and ranking path is exercised by the
`api-postgres` CI job.

The GIN index is created by the `c4a1f2d3e5b6` migration only when the dialect is
PostgreSQL. `alembic check` on SQLite does not compare it.

### Concurrency and oversell protection

`reserve_stock` and `release_stock` are single conditional `UPDATE` statements
(`WHERE on_hand - reserved >= :quantity`). This is the oversell guard and it is
correct on both engines.

* **PostgreSQL** uses row-level locks. Two concurrent reservations for the last
  unit serialise on the inventory row: one updates, the other sees
  `rowcount == 0` and gets `OutOfStock`.
* **SQLite** serialises writers with a database-level write lock and
  `busy_timeout=30000`. The same conditional update wins or loses the same way,
  but there is no true row-level concurrency, so a high-contention test proves
  less. `PRAGMA journal_mode=WAL` is set for the local file.

Concurrent last-unit orders are tested in the `api-postgres` CI job. Locally
they run on SQLite and pass, but they do not exercise real row locks.

### Transactions and isolation

* PostgreSQL defaults to `READ COMMITTED`; SQLite serialises writes. A
  read-then-write sequence in application code is therefore not a safe oversell
  guard on either engine. All stock changes use the conditional update instead
  of read-then-write.
* PostgreSQL rolls back DDL; SQLite does not. A failed migration can leave a
  SQLite file half-changed, so migrations are verified by upgrading and
  downgrading a fresh database.

### Case sensitivity

`ILIKE` is case-insensitive on PostgreSQL for the database locale. SQLite's
`LIKE`/`ILIKE` is case-insensitive for ASCII only, so accented characters and
non-Latin scripts can compare differently. The catalogue is ASCII today; this
will matter when Hindi product copy is added.

### Data types

* Money is stored as `NUMERIC(10, 2)` and handled as `Decimal`. Both engines
  preserve scale, but SQLite has no native decimal type, so it stores the value
  as text/real depending on affinity. Rounding is done in Python, never by the
  database, so totals are identical.
* `DateTime(timezone=True)` keeps UTC offsets on PostgreSQL. SQLite stores the
  string as given, so comparisons rely on consistent UTC writes. All timestamps
  are written as timezone-aware UTC.
* `JSON` columns are native `json` on PostgreSQL and text on SQLite. The
  application always reads through SQLAlchemy, so both deserialise the same.

### Constraints and indexes

* `CHECK` constraints, foreign keys and unique indexes are enforced on both.
  SQLite needs `PRAGMA foreign_keys=ON`, which `db.py` sets on every connection.
* Partial indexes and expression indexes are PostgreSQL-only. None are used in
  application queries.
* Alembic uses `render_as_batch=True` so SQLite can recreate tables for
  `ALTER COLUMN`, `DROP COLUMN` and constraint changes. PostgreSQL applies the
  statements directly.

### DDL in migrations

SQLite cannot `ALTER COLUMN ... SET NOT NULL` or drop a column in place.
Migrations that need those operations use `op.batch_alter_table`, which recreates
the table on SQLite and emits normal `ALTER TABLE` on PostgreSQL. The
`d5b2e8f1a3c7` cart migration is the first to rely on this.

## What CI covers

| Job | Database | Purpose |
| --- | --- | --- |
| `api-sqlite` | SQLite | Fast feedback on the portable paths |
| `api-postgres` | PostgreSQL 16 | Full suite, real row locks, FTS and GIN index, `alembic upgrade head && alembic check` |

If a test passes on SQLite and fails on PostgreSQL, the difference is almost
always search semantics or a locking assumption. Fix the query, not the test.
