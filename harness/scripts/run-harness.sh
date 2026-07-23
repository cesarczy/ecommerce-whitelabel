#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILURES=0
WARNINGS=0

pass() { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; FAILURES=$((FAILURES + 1)); }
warn() { echo -e "${YELLOW}!${NC} $1"; WARNINGS=$((WARNINGS + 1)); }

echo "═══════════════════════════════════════"
echo "  Cursor Clean DDD Kit — Harness"
echo "  Root: $ROOT"
echo "═══════════════════════════════════════"
echo

echo "── Specs ──"
SPEC_COUNT=$(find specs -name '*.spec.md' 2>/dev/null | wc -l)
if [ "$SPEC_COUNT" -eq 12 ]; then pass "12 specs presentes"; else fail "Esperado 12 specs, encontrado $SPEC_COUNT"; fi

echo "── Rules ──"
RULE_COUNT=$(find .cursor/rules -name '*.mdc' 2>/dev/null | wc -l)
if [ "$RULE_COUNT" -ge 10 ]; then pass "$RULE_COUNT rules configuradas"; else warn "Poucas rules ($RULE_COUNT)"; fi

echo "── Layer Dependencies ──"
bash "$ROOT/harness/scripts/check-layer-dependencies.sh" || FAILURES=$((FAILURES + 1))

echo "── DDD Compliance ──"
bash "$ROOT/harness/scripts/check-ddd-compliance.sh" || FAILURES=$((FAILURES + 1))

echo "── ORM Isolation ──"
bash "$ROOT/harness/scripts/check-prisma-schema.sh" || FAILURES=$((FAILURES + 1))

echo "── Architecture ──"
bash "$ROOT/harness/scripts/check-architecture.sh" || FAILURES=$((FAILURES + 1))

echo
echo "═══════════════════════════════════════"
if [ "$FAILURES" -eq 0 ]; then echo -e "${GREEN}HARNESS: PASS${NC} ($WARNINGS warnings)"; exit 0
else echo -e "${RED}HARNESS: FAIL${NC} ($FAILURES failures, $WARNINGS warnings)"; exit 1; fi
