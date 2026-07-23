#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FORBIDDEN='@prisma/client|from ['\''"]express|from ['\''"]fastify|from ['\''"]react|from ['\''"]next'
VIOLATIONS=0
DOMAIN_DIRS=$(find "$ROOT/src" -type d -name domain 2>/dev/null || true)
[ -z "$DOMAIN_DIRS" ] && { echo "  (sem domain — OK)"; exit 0; }
while IFS= read -r dir; do
  if rg -l "$FORBIDDEN" "$dir" --glob '*.ts' --glob '*.tsx' 2>/dev/null; then
    echo "  VIOLAÇÃO: import proibido em $dir"; VIOLATIONS=$((VIOLATIONS + 1))
  fi
  if rg -l "from ['\"].*infrastructure" "$dir" --glob '*.ts' 2>/dev/null; then
    echo "  VIOLAÇÃO: domain importa infrastructure em $dir"; VIOLATIONS=$((VIOLATIONS + 1))
  fi
done <<< "$DOMAIN_DIRS"
[ "$VIOLATIONS" -gt 0 ] && exit 1
echo "  Layer dependencies OK"
exit 0
