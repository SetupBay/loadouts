#!/usr/bin/env bash
# PostToolUse hook for Edit|Write: a fast check on the one file that changed.
# Exit 2 sends stderr back to the agent so it fixes the file before moving on. Missing tools are skipped.
set -u
input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')
[ -n "$file" ] && [ -f "$file" ] || exit 0
have() { command -v "$1" >/dev/null 2>&1; }
root="${CLAUDE_PROJECT_DIR:-$PWD}"
out=""
case "$file" in
  *.sh|*.bash) out=$(bash -n "$file" 2>&1) ;;
  *.json) if have jq; then out=$(jq empty "$file" 2>&1); fi ;;
  *.py)
    if have ruff; then out=$(ruff check --quiet "$file" 2>&1)
    elif have python3; then out=$(python3 -m py_compile "$file" 2>&1); fi ;;
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs)
    if [ -x "$root/node_modules/.bin/eslint" ]; then out=$("$root/node_modules/.bin/eslint" --no-warn-ignored "$file" 2>&1)
    elif [[ "$file" =~ \.(js|mjs|cjs)$ ]] && have node; then out=$(node --check "$file" 2>&1); fi ;;
esac
status=$?
if [ $status -ne 0 ]; then
  printf 'post-edit check failed for %s:\n%s\n' "$file" "$(printf '%s' "$out" | tail -n 30)" >&2
  exit 2
fi
exit 0
