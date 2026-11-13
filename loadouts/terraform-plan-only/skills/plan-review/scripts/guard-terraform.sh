#!/usr/bin/env bash
# PreToolUse hook for Bash (Claude Code). Denies Terraform / OpenTofu commands that change real infrastructure or state.
# Reads the tool call as JSON on stdin; prints a deny decision with a reason, or nothing. Needs jq.
set -u
cmd=$(jq -r '.tool_input.command // empty')
[ -z "$cmd" ] && exit 0
flat=$(printf '%s' "$cmd" | tr '\n\t' '  ' | tr '[:upper:]' '[:lower:]')

deny() {
  jq -n --arg r "Blocked by guard-terraform: $1" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  exit 0
}

tf='(^|[[:space:];&|(/])(terraform|tofu|terragrunt)[[:space:]]+([^;&|]*[[:space:]])?'
[[ "$flat" =~ -auto-approve ]] && deny "-auto-approve skips the human review. Produce a plan and hand it over."
[[ "$flat" =~ ${tf}(apply|destroy)([[:space:]]|$) ]] && deny "apply and destroy change real infrastructure. Show the plan; the human runs it."
[[ "$flat" =~ ${tf}(import|taint|untaint|force-unlock)([[:space:]]|$) ]] && deny "this changes state. Ask the human."
[[ "$flat" =~ ${tf}state[[:space:]]+(rm|mv|push|replace-provider)([[:space:]]|$) ]] && deny "state changes can orphan or destroy resources. Ask the human."
[[ "$flat" =~ ${tf}workspace[[:space:]]+delete([[:space:]]|$) ]] && deny "deleting a workspace loses its state. Ask the human."
[[ "$flat" =~ \.tfstate([[:space:]]|$|\.backup) && "$flat" =~ (^|[[:space:]])(cat|less|more|head|tail|cp|mv|rm|vi|vim|nano|sed)[[:space:]] ]] && deny "state files hold secrets. Use terraform show or terraform state list."
exit 0
