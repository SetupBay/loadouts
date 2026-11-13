---
name: plan-review
description: Produce and summarise a Terraform plan, flag every delete and replace, and install a hook that blocks apply and destroy. Use after any Terraform change, before handing it to a human.
---

# Plan review

1. `terraform fmt -recursive` and `terraform validate`. Fix everything they report.
2. Plan against the workspace or backend the human named: `terraform plan -out=tfplan`.
3. Summarise: `terraform show -json tfplan > plan.json` then `bash scripts/plan-summary.sh plan.json`.
   It prints counts of create, update, replace and delete, lists every replace and delete by address, and exits 1 if
   there are any. Delete `plan.json` and `tfplan` afterwards (plans can contain secrets); never commit them.
4. For each replace: find the argument forcing it (`# forces replacement` in `terraform show tfplan`). Prefer a
   `moved` block or an in-place change; if a replace is really needed, say why.
5. Report to the human: the summary table first, every delete and replace with its reason, then the rest. End with the
   exact apply command for them to run. Do not run it.

## Guard hook (Claude Code)
Copy `scripts/guard-terraform.sh` to the project's hooks folder and register it as a PreToolUse hook on Bash, as in
`references/settings.example.json`, with `onFailure: "block"`. It denies apply, destroy, state changes, import,
force-unlock and `-auto-approve` for both `terraform` and `tofu`, with a reason. Test it:
`bash scripts/selftest.sh`.
