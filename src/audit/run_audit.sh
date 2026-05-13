#!/usr/bin/env bash
set -euo pipefail

MODULE_ID="${1:?Usage: ./run_audit.sh <module_id> [round]}"
ROUND="${2:-1}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

LOG_DIR="$PROJECT_ROOT/audit_log/$MODULE_ID"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d)_round_${ROUND}.yaml"

PROMPT=$(PYTHONPATH="$PROJECT_ROOT/src" ./.venv/bin/python -m audit.tools.assemble_contract_audit "$MODULE_ID")

echo "$PROMPT" | claude -p --model claude-opus-4-7 --effort xhigh | tee "$LOG_FILE"

echo "" >&2
echo "Audit log saved: $LOG_FILE" >&2
