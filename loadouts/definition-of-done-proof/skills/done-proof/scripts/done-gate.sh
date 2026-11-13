#!/usr/bin/env bash
# Claude Code Stop hook: refuse "done" while test files were weakened, skipped or deleted.
# Exit 2 keeps Claude working and shows it the findings. Respects stop_hook_active so it never loops.
# Base ref: DONE_PROOF_BASE (default HEAD, i.e. this session's uncommitted changes).
set -u
input=$(cat)
printf '%s' "$input" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("stop_hook_active") else 1)' 2>/dev/null && exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
script="${CLAUDE_PROJECT_DIR:-.}/.claude/skills/done-proof/scripts/test_tamper.py"
[ -f "$script" ] || script=".agents/skills/done-proof/scripts/test_tamper.py"
[ -f "$script" ] || exit 0
if ! out=$(python3 "$script" --base "${DONE_PROOF_BASE:-HEAD}" 2>&1); then
  printf 'You changed tests to make them pass. You are not done:\n%s\n' "$out" >&2
  exit 2
fi
exit 0
