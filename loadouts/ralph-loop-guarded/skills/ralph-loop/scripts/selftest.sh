#!/usr/bin/env bash
# Runs ralph.sh against fake agents in throwaway repositories and checks every exit path.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
runner="$here/ralph.sh"
pass=0; failed=0

repo() {
  local d; d="$(mktemp -d)"
  ( cd "$d" && git init -q -b main && git config user.email t@example.com && git config user.name t \
    && mkdir .ralph && echo "goal" > .ralph/prompt.md && echo "- [ ] a" > .ralph/plan.md && : > .ralph/progress.md \
    && git add -A && git commit -qm init && git switch -qc ralph/test )
  echo "$d"
}
expect() { # name, want-exit, dir, env...
  local name="$1" want="$2" d="$3"; shift 3
  ( cd "$d" && env MAX_ITER=4 PASS_TIMEOUT=20 "$@" bash "$runner" > out.txt 2>&1 ); local got=$?
  if [ "$got" -eq "$want" ]; then pass=$((pass + 1)); else failed=$((failed + 1)); echo "FAIL: $name (exit $got, wanted $want)"; cat "$d/out.txt"; fi
}

d="$(repo)"; ( cd "$d" && git switch -q main )
expect "refuses main" 5 "$d" AGENT_CMD=true CHECK_CMD=true

d="$(repo)"
expect "idle agent stops on no progress" 3 "$d" AGENT_CMD=true CHECK_CMD=true

d="$(repo)"
expect "busy agent hits the iteration limit" 2 "$d" 'AGENT_CMD=date +%s%N >> work.txt && git add work.txt && git commit -qm pass' CHECK_CMD=true

d="$(repo)"
expect "DONE with a green check exits 0" 0 "$d" 'AGENT_CMD=echo ok > .ralph/DONE' CHECK_CMD=true

d="$(repo)"
expect "false DONE is removed and the loop goes on" 3 "$d" 'AGENT_CMD=echo ok > .ralph/DONE' CHECK_CMD=false
grep -q "false DONE removed" "$d/.ralph/progress.md" && pass=$((pass + 1)) || { failed=$((failed + 1)); echo "FAIL: false DONE not logged"; }

d="$(repo)"
expect "editing the prompt stops the loop" 5 "$d" 'AGENT_CMD=echo cheat >> .ralph/prompt.md' CHECK_CMD=true

d="$(repo)"; touch "$d/.ralph/STOP"
expect "STOP file stops the loop" 4 "$d" AGENT_CMD=true CHECK_CMD=true

d="$(repo)"
expect "a pass that hangs is timed out" 3 "$d" 'AGENT_CMD=sleep 30' CHECK_CMD=true PASS_TIMEOUT=1
grep -q "timed out" "$d/.ralph/progress.md" && pass=$((pass + 1)) || { failed=$((failed + 1)); echo "FAIL: timeout not logged"; }

if [ "$failed" -eq 0 ]; then echo "ok: $pass cases"; else echo "failed: $failed of $((pass + failed))"; exit 1; fi
