#!/usr/bin/env bash
# Summarise `terraform show -json tfplan` output. Exit 1 if anything is deleted or replaced. Needs jq.
set -euo pipefail
plan="${1:?usage: plan-summary.sh plan.json}"
jq -r '
  def kind: if . == ["create"] then "create"
    elif . == ["update"] then "update"
    elif . == ["delete"] then "delete"
    elif (. == ["delete","create"] or . == ["create","delete"]) then "replace"
    else "no-op" end;
  [.resource_changes[]? | {address, kind: (.change.actions | kind)}] as $c
  | "create: \([$c[] | select(.kind == "create")] | length)",
    "update: \([$c[] | select(.kind == "update")] | length)",
    "replace: \([$c[] | select(.kind == "replace")] | length)",
    "delete: \([$c[] | select(.kind == "delete")] | length)",
    ($c[] | select(.kind == "replace" or .kind == "delete") | "\(.kind | ascii_upcase): \(.address)")
' "$plan"
if jq -e '[.resource_changes[]? | .change.actions | select(index("delete"))] | length > 0' "$plan" >/dev/null; then
  echo "plan destroys or replaces resources: review each one above before anyone applies"
  exit 1
fi
echo "plan has no deletes or replaces"
