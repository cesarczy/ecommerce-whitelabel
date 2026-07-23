#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VIOLATIONS=0

while IFS= read -r file; do
  echo "$file" | grep -qE 'infra/|core/database|api/deps|application/queries|main\.py' && continue
  echo "  VIOLAÇÃO: sqlalchemy em $file (fora de infra)"; VIOLATIONS=$((VIOLATIONS + 1))
done < <(rg -l 'sqlalchemy' "$ROOT/backend/app" --glob '*.py' 2>/dev/null | grep -v '/infra/' || true)

if [ -f "$ROOT/backend/alembic.ini" ]; then
  echo "  Alembic configurado"
fi

[ "$VIOLATIONS" -gt 0 ] && exit 1
echo "  ORM isolation OK"
exit 0
