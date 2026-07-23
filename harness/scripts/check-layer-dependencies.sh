#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FORBIDDEN='sqlalchemy|fastapi|redis|celery|minio|asyncpg'
VIOLATIONS=0

if [ -d "$ROOT/backend/app/domain" ]; then
  while IFS= read -r file; do
    echo "  VIOLAÇÃO: import proibido em $file"; VIOLATIONS=$((VIOLATIONS + 1))
  done < <(rg -l "$FORBIDDEN" "$ROOT/backend/app/domain" --glob '*.py' 2>/dev/null || true)
  while IFS= read -r file; do
    echo "  VIOLAÇÃO: domain importa infra em $file"; VIOLATIONS=$((VIOLATIONS + 1))
  done < <(rg -l "from app\.infra|import app\.infra" "$ROOT/backend/app/domain" --glob '*.py' 2>/dev/null || true)
fi

if [ -d "$ROOT/src" ]; then
  bash "$ROOT/harness/scripts/check-layer-dependencies.sh" || VIOLATIONS=$((VIOLATIONS + 1))
fi

[ "$VIOLATIONS" -gt 0 ] && exit 1
echo "  Layer dependencies OK"
exit 0
