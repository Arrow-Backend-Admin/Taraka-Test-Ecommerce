#!/usr/bin/env bash
# Back up the configured database. PostgreSQL uses pg_dump custom format;
# SQLite is copied file-for-file. Never prints the database URL.
#
#   DATABASE_URL=postgresql+psycopg://... ./scripts/backup_db.sh
#   BACKUP_DIR=/var/backups/santvana ./scripts/backup_db.sh
set -euo pipefail

API_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$API_ROOT"

DATABASE_URL="${DATABASE_URL:-}"
if [[ -z "$DATABASE_URL" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 2
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="${BACKUP_DIR:-backups}"
EXT="dump"
if [[ "$DATABASE_URL" == sqlite* ]]; then
  EXT="sqlite"
fi
OUTPUT="${BACKUP_DIR}/santvana-${STAMP}.${EXT}"

python - "$DATABASE_URL" "$OUTPUT" <<'PY'
import sys
from app.services.backup import dump_database

url, output = sys.argv[1], sys.argv[2]
path = dump_database(url, output)
print(f"Backup written to {path}")
PY
