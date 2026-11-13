# AGENTS.md

OpenTofu 1.13 modules and environments for AWS. Agents **plan only**; humans apply.

## Commands
- Format: `tofu fmt -recursive`
- Validate a module: `cd modules/<name> && tofu init -backend=false && tofu validate`
- Plan an environment: `cd envs/staging && tofu init && tofu plan -out=plan.bin` (read-only credentials)
- Policy scan: `checkov -d modules --quiet`

## Layout
- `modules/` reusable modules with `variables.tf`, `outputs.tf`, `README.md`; `envs/<env>/` one root per environment

## Rules
- Pin providers with `~>` in `versions.tf`; commit `.terraform.lock.hcl`
- Every new variable has a type, a description and validation where it can be wrong
- Tag every resource through the module's `tags` variable

## Never
- Run `tofu apply`, `tofu destroy`, `tofu state` or `tofu import`; ask the human
- Put secrets in `.tf` or `.tfvars` files; use the secrets manager data source
- Edit `envs/production/` unless the task names it

## Done means
`tofu fmt -check`, `tofu validate` and `checkov` pass, and the plan output for the changed environment is in your
report with every create, change and destroy listed.
