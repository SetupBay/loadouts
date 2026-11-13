#!/usr/bin/env bash
# Guarded Ralph loop: one fresh agent process per pass, state in .ralph/, hard limits, check run outside the agent.
# Exit codes: 0 done, 2 iteration limit, 3 no progress, 4 stopped by .ralph/STOP, 5 refused to start or prompt edited.
set -uo pipefail

: "${AGENT_CMD:?set AGENT_CMD, for example: claude -p --permission-mode acceptEdits < \"\$RALPH_PROMPT\"}"
: "${CHECK_CMD:?set CHECK_CMD, for example: npm test}"
MAX_ITER="${MAX_ITER:-10}"
MAX_NO_PROGRESS="${MAX_NO_PROGRESS:-2}"
PASS_TIMEOUT="${PASS_TIMEOUT:-1800}"
DIR=".ralph"
export RALPH_PROMPT="$DIR/prompt.md"

say() { printf 'ralph: %s\n' "$*"; }
log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$DIR/progress.md"; }
state() { printf '%s %s' "$(git rev-parse HEAD 2>/dev/null)" "$(git status --porcelain=v1 -- . ":(exclude)$DIR/log" | sha256sum | cut -c1-16)"; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { say "not a git repository"; exit 5; }
branch="$(git symbolic-ref --quiet --short HEAD || true)"
case "$branch" in
  ""|main|master) say "refusing to run on '${branch:-detached HEAD}'; create a ralph/<task> branch first"; exit 5 ;;
esac
[ -f "$RALPH_PROMPT" ] || { say "missing $RALPH_PROMPT"; exit 5; }
mkdir -p "$DIR/log"
prompt_hash="$(sha256sum "$RALPH_PROMPT" | cut -c1-64)"
no_progress=0

for ((i = 1; i <= MAX_ITER; i++)); do
  if [ -f "$DIR/STOP" ]; then say "stop file found before pass $i"; log "stopped by .ralph/STOP"; exit 4; fi
  before="$(state)"
  say "pass $i/$MAX_ITER"
  timeout "$PASS_TIMEOUT" bash -c "$AGENT_CMD" > "$DIR/log/pass-$i.txt" 2>&1
  rc=$?
  [ "$rc" -eq 124 ] && log "pass $i timed out after ${PASS_TIMEOUT}s"

  if [ "$(sha256sum "$RALPH_PROMPT" | cut -c1-64)" != "$prompt_hash" ]; then
    say "pass $i edited $RALPH_PROMPT; stopping"; log "pass $i edited the prompt; loop stopped"; exit 5
  fi

  if [ -f "$DIR/DONE" ]; then
    if bash -c "$CHECK_CMD" > "$DIR/log/check-$i.txt" 2>&1; then
      say "done after $i pass(es); check passed"; log "done after $i passes; check passed"; exit 0
    fi
    say "pass $i wrote DONE but the check fails; removing DONE"; rm -f "$DIR/DONE"; log "pass $i: false DONE removed (check failed)"
  fi

  if [ "$(state)" = "$before" ]; then
    no_progress=$((no_progress + 1))
    say "no change in pass $i ($no_progress/$MAX_NO_PROGRESS)"
    if [ "$no_progress" -ge "$MAX_NO_PROGRESS" ]; then log "no progress for $no_progress passes; loop stopped"; exit 3; fi
  else
    no_progress=0
  fi
done
say "iteration limit ($MAX_ITER) reached"; log "iteration limit $MAX_ITER reached"; exit 2
