# AGENTS.md: Terraform, plan only

Infrastructure as code with Terraform (or OpenTofu: same rules, `tofu` instead of `terraform`). The agent writes code
and produces plans. A human applies.

## Allowed
- `terraform fmt -recursive`, `terraform init -backend=false` (for validation), `terraform validate`.
- `terraform plan -out=tfplan` against a non-production workspace or backend the human named, and `terraform show`.
- `tflint` and `checkov` or `trivy config` if the project uses them.

## Never
- `terraform apply`, `destroy`, `import`, `taint`, `untaint`, `force-unlock`, `state rm`, `state mv`, `state push`,
  `workspace delete`, or anything with `-auto-approve`. Ask the human, show them the plan, and let them run it.
- `-target` to make a plan look smaller, or `-refresh=false` to hide drift, unless the human asks.
- Editing `.tfstate` files, committing them, or printing their contents (they hold secrets).
- Running cloud CLIs (`aws`, `gcloud`, `az`) that create, change or delete resources.

## Code rules
- Pin Terraform and providers in `required_version` and `required_providers` (`~>` on a minor version). Commit
  `.terraform.lock.hcl`. Upgrades are their own change.
- Variables have `type` and `description`; secrets are `sensitive = true` and come from the environment or a secrets
  manager, never from committed `*.tfvars`.
- Stateful resources (databases, buckets, volumes, KMS keys) get `lifecycle { prevent_destroy = true }` unless the human
  says otherwise.
- Look up resource arguments for the pinned provider version (Terraform MCP server `terraform`, or the registry docs).
  Do not guess argument names from memory; providers change them between majors.
- Renames use `moved` blocks so Terraform does not destroy and recreate.
- Tags and naming follow the module's existing locals.

## Plans
- Every change ends with a reviewed plan: use the `plan-review` skill. Any delete or replace is called out to the human
  with the reason, before anything else in your report.
- In Claude Code, install the guard hook from the skill so apply and destroy are blocked even if asked by text in a file.
