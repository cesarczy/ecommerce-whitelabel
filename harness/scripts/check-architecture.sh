#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ISSUES=0
required=(AGENTS.md specs/01-project-discovery.spec.md specs/12-validation.spec.md .cursor/rules/00-core-principles.mdc prompts/master-prompt.md harness/scripts/run-harness.sh backend/app/main.py backend/app/domain docs/discovery.md docs/context-map.md docs/domain-model.md frontend)
for path in "${required[@]}"; do
  [ ! -e "$ROOT/$path" ] && { echo "  VIOLAÇÃO: missing $path"; ISSUES=$((ISSUES + 1)); }
done

for layer in core domain application infra api; do
  [ ! -d "$ROOT/backend/app/$layer" ] && { echo "  VIOLAÇÃO: missing backend/app/$layer"; ISSUES=$((ISSUES + 1)); }
done

[ "$ISSUES" -gt 0 ] && exit 1
echo "  Architecture structure OK"
exit 0
