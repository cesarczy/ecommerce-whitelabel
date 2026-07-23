#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ISSUES=0
[ ! -d "$ROOT/src" ] && { echo "  (sem src — OK)"; exit 0; }
UC_DIR=$(find "$ROOT/src" -type d -name use-cases 2>/dev/null || true)
if [ -n "$UC_DIR" ]; then
  while IFS= read -r dir; do
    for f in "$dir"/*.ts; do
      [ -f "$f" ] || continue
      base=$(basename "$f")
      if [[ "$base" != *.use-case.ts ]] && [[ "$base" != "index.ts" ]]; then
        echo "  VIOLAÇÃO: $f deve usar sufixo .use-case.ts"; ISSUES=$((ISSUES + 1))
      fi
    done
  done <<< "$UC_DIR"
fi
DOMAIN_DIRS=$(find "$ROOT/src" -type d -name domain 2>/dev/null || true)
if [ -n "$DOMAIN_DIRS" ]; then
  while IFS= read -r dir; do
    if find "$dir" -name '*.service.ts' 2>/dev/null | grep -q .; then
      echo "  VIOLAÇÃO: *.service.ts em domain ($dir)"; ISSUES=$((ISSUES + 1))
    fi
  done <<< "$DOMAIN_DIRS"
fi
[ "$ISSUES" -gt 0 ] && exit 1
echo "  DDD conventions OK"
exit 0
