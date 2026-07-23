#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VIOLATIONS=0

if [ -d "$ROOT/backend/app/domain" ]; then
  if find "$ROOT/backend/app/domain" -name '*_service.py' 2>/dev/null | grep -q .; then
    echo "  VIOLAÇÃO: *_service.py em domain"; VIOLATIONS=$((VIOLATIONS + 1))
  fi
  if find "$ROOT/backend/app/application/commands" -name '*.py' ! -name '__init__.py' 2>/dev/null | grep -q .; then
    echo "  Use cases presentes em application/commands"
  fi
fi

[ "$VIOLATIONS" -gt 0 ] && exit 1
echo "  DDD conventions OK"
exit 0
