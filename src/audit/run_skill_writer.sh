#!/usr/bin/env bash
set -euo pipefail

MODULE_ID="${1:?Usage: ./run_skill_writer.sh <module_id> <skill_dir>}"
SKILL_DIR="${2:?Usage: ./run_skill_writer.sh <module_id> <skill_dir>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

PROMPT=$(PYTHONPATH="$PROJECT_ROOT/src" ./.venv/bin/python -m audit.tools.assemble_skill_writer "$MODULE_ID" "$SKILL_DIR")

echo "$PROMPT" | claude -p --model claude-opus-4-7 --effort xhigh
