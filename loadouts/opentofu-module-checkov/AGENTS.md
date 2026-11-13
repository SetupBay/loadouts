# AGENTS.md: OpenTofu modules gated by tofu test and Checkov

Infrastructure as code in OpenTofu (HCL works the same in Terraform, with `terraform` for `tofu`). Check
`required_providers` and the lock file before using a provider argument: AWS provider v6 split many bucket
settings into separate resources.

## Commands
- Format: `tofu fmt -recursive`.
- Gate (run before calling a change done): `bash .agents/skills/tofu-module-gate/scripts/gate.sh <module-dir>`.
  It runs fmt check, `tofu init -backend=false -lockfile=readonly`, `tofu validate`, `tofu test` and Checkov, and
  needs no cloud credentials.
- Done means: `gate: ok`, with a `run` block in `tests/` covering the behaviour you changed.

## Rules
- Use the `tofu-module-gate` skill for any change to `.tf` or `.tftest.hcl` files.
- Never run `tofu apply`, `destroy`, `import`, `state` subcommands, `force-unlock` or `-auto-approve`, and never
  read state files. A person plans against real accounts and applies.
- Tests use `mock_provider`. Do not add real credentials, profiles or a backend to make a test pass.
- Every variable has a description and a type; constrained inputs have a `validation` block and a test with
  `expect_failures`.
- Pin providers (`~>` on a minor version) and keep the committed lock file. Upgrading a provider is its own change,
  stated in the summary.
- Fix Checkov findings. An exception is an inline `#checkov:skip=<ID>:<reason>` on the resource, never
  `soft-fail`, `--skip-check` or a repo-wide skip list.
- Root modules enforce OpenTofu state and plan encryption, with the key from the environment or a KMS key
  provider, never from a file.
- Stateful resources (buckets, databases, keys) carry `prevent_destroy = true`. Renames use `moved` blocks.
