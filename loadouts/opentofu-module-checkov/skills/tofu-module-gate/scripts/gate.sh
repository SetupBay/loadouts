#!/usr/bin/env bash
# Module gate: fmt, init (lock file read-only), validate, tofu test, Checkov, and an audit of
# Checkov exceptions. Runs no plan against real cloud accounts and never applies.
# Usage: gate.sh [module-dir]   (default: current directory)
# Env: TOFU (default tofu), CHECKOV (default: uvx --from checkov==3.3.29 checkov)
set -uo pipefail

dir="${1:-.}"
TOFU="${TOFU:-tofu}"
CHECKOV="${CHECKOV:-uvx --from checkov==3.3.29 checkov}"
cd "$dir" || { echo "gate: no such directory: $dir"; exit 2; }

fail() { echo "gate: FAILED at $1"; exit 1; }
step() { echo "== $1"; }

step "fmt"
"$TOFU" fmt -check -recursive -diff -no-color || fail "fmt (run: tofu fmt -recursive)"

step "init"
[ -f .terraform.lock.hcl ] || fail "init (no .terraform.lock.hcl: run tofu init and commit the lock file)"
"$TOFU" init -backend=false -input=false -lockfile=readonly -no-color >/dev/null || fail "init"

step "validate"
"$TOFU" validate -no-color || fail "validate"

step "test"
if ls tests/*.tftest.hcl >/dev/null 2>&1; then
  "$TOFU" test -no-color || fail "test"
else
  fail "test (no tests/*.tftest.hcl)"
fi

step "exception audit"
bad=0
if [ -f .checkov.yaml ] && grep -Eq '^[[:space:]]*(soft-fail|soft_fail)[[:space:]]*:[[:space:]]*true' .checkov.yaml; then
  echo "soft-fail is set in .checkov.yaml: findings would not fail the run"; bad=1
fi
if [ -f .checkov.yaml ] && grep -Eq '^[[:space:]]*skip-check[[:space:]]*:' .checkov.yaml; then
  echo "skip-check in .checkov.yaml hides checks repo-wide: use an inline skip with a reason"; bad=1
fi
while IFS= read -r hit; do
  reason="${hit#*checkov:skip=}"; reason="${reason#*:}"
  if [ "$reason" = "${hit#*checkov:skip=}" ] || [ "${#reason}" -lt 10 ]; then
    echo "skip without a reason: $hit"; bad=1
  fi
done < <(grep -rn --include='*.tf' 'checkov:skip=' . | grep -v '/\.terraform/')
[ "$bad" -eq 0 ] || fail "exception audit"

step "checkov"
cfg=()
[ -f .checkov.yaml ] && cfg=(--config-file .checkov.yaml)
# shellcheck disable=SC2086
$CHECKOV -d . "${cfg[@]}" --framework terraform --compact --quiet || fail "checkov"

echo "gate: ok"
