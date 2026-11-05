#!/usr/bin/env bash
# Restore a backup produced by backup_db.sh. This is destructive: pg_restore
# runs with --clean and drops objects in the target database first.
#
#   DATABASE_URL=postgresql+psycopg://... ./scripts/restore_db.sh backup.dump
set -euo pipefail

API_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$API_ROOT"

DUMP="${1:-}"
DATABASE_URL="${DATABASE_URL:-}"
if [[ -z "$DUMP" ]]; then
  echo "Usage: DATABASE_URL=... $0 <backup-file>" >&2
  exit 2
fi
if [[ -z "$DATABASE_URL" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 2
fi

python - "$DATABASE_URL" "$DUMP" <<'PY'
import sys
from app.services.backup import restore_database

url, dump = sys.argv[1], sys.argv[2]
restore_database(url, dump)
print(f"Restored {dump} into the target database")
PY
