#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VIOLATIONS=0
[ ! -d "$ROOT/src" ] && { echo "  (sem src — OK)"; exit 0; }
while IFS= read -r file; do
  echo "$file" | grep -qE 'infrastructure|/prisma/' && continue
  echo "  VIOLAÇÃO: @prisma/client em $file (fora de infrastructure)"; VIOLATIONS=$((VIOLATIONS + 1))
done < <(rg -l '@prisma/client' "$ROOT/src" --glob '*.ts' 2>/dev/null || true)
if [ -f "$ROOT/prisma/schema.prisma" ] && command -v npx &>/dev/null && [ -f "$ROOT/package.json" ]; then
  (cd "$ROOT" && npx prisma validate 2>/dev/null) && echo "  prisma validate OK" || { echo "  VIOLAÇÃO: prisma validate failed"; VIOLATIONS=$((VIOLATIONS + 1)); }
fi
[ "$VIOLATIONS" -gt 0 ] && exit 1
echo "  Prisma isolation OK"
exit 0
