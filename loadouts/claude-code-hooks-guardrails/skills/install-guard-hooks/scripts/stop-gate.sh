#!/usr/bin/env bash
# Stop hook: run the project's tests once when the agent says it is done.
# Exit 2 keeps the agent working and shows it the failures. Respects stop_hook_active (Claude Code, Codex)
# and loop_count (Cursor) so it never loops.
set -u
input=$(cat)
[ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false')" = "true" ] && exit 0
# Cursor sends loop_count instead, and sets no loop limit on hooks it loads from .claude/settings.json.
[ "$(printf '%s' "$input" | jq -r '.loop_count // 0')" -ge 2 ] 2>/dev/null && exit 0
root="${CLAUDE_PROJECT_DIR:-$(printf '%s' "$input" | jq -r '.cwd // empty')}"
cd "${root:-.}" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
[ -z "$(git status --porcelain 2>/dev/null)" ] && exit 0   # nothing changed, nothing to gate

test_cmd="${GUARD_TEST_CMD:-}"
[ -z "$test_cmd" ] && [ -f .claude/hooks/test-command ] && test_cmd=$(head -n 1 .claude/hooks/test-command)
if [ -z "$test_cmd" ]; then
  if [ -f package.json ] && jq -e '.scripts.test' package.json >/dev/null 2>&1; then test_cmd="npm test --silent"
  elif [ -f pyproject.toml ] && command -v pytest >/dev/null 2>&1; then test_cmd="pytest -q"
  elif [ -f Cargo.toml ]; then test_cmd="cargo test -q"
  elif [ -f go.mod ]; then test_cmd="go test ./..."
  else exit 0; fi
fi
runner=(bash -c "$test_cmd")
command -v timeout >/dev/null 2>&1 && runner=(timeout "${GUARD_TEST_TIMEOUT:-600}" bash -c "$test_cmd")
if ! out=$("${runner[@]}" 2>&1); then
  printf 'Tests failed (%s). You are not done; fix the cause:\n%s\n' "$test_cmd" "$(printf '%s' "$out" | tail -n 40)" >&2
  exit 2
fi
exit 0
