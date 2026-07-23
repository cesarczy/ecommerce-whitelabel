#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ISSUES=0
required=(AGENTS.md specs/01-project-discovery.spec.md specs/12-validation.spec.md .cursor/rules/00-core-principles.mdc prompts/master-prompt.md harness/scripts/run-harness.sh)
for path in "${required[@]}"; do
  [ ! -e "$ROOT/$path" ] && { echo "  VIOLAÇÃO: missing $path"; ISSUES=$((ISSUES + 1)); }
done
if [ -d "$ROOT/src/modules" ]; then
  for mod in "$ROOT/src/modules"/*; do
    [ -d "$mod" ] || continue
    for layer in domain application infrastructure presentation; do
      [ ! -d "$mod/$layer" ] && { echo "  VIOLAÇÃO: $mod missing layer $layer"; ISSUES=$((ISSUES + 1)); }
    done
  done
fi
[ "$ISSUES" -gt 0 ] && exit 1
echo "  Architecture structure OK"
exit 0
