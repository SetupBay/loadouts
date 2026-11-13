---
name: tofu-module-gate
description: Write or change an OpenTofu (or Terraform) module so it passes a local gate - fmt, validate, tofu test with a mocked provider, and Checkov with reasoned exceptions only. Use when adding or editing .tf files, module variables, tests, or Checkov skips.
---

# OpenTofu module gate

A module change is done when `scripts/gate.sh` prints `gate: ok`. The gate needs no cloud
credentials and creates nothing: tests run against `mock_provider`, Checkov reads the HCL.

## Workflow

1. Read the module's variables, outputs and tests before editing. Keep one resource type per
   concern (the bucket, its versioning, its encryption ...), as the AWS provider v6 expects.
2. Make the change. Every new input gets a `description`, a `type`, and a `validation` block
   when it has a valid range or format.
3. Add or update a `run` block in `tests/*.tftest.hcl` for the behaviour you changed:
   - `command = plan` with `assert` blocks for secure defaults and computed values;
   - `expect_failures = [var.x]` for every validation rule you add.
4. Run the gate on the module folder:

   ```bash
   TOFU=tofu bash .agents/skills/tofu-module-gate/scripts/gate.sh modules/s3-bucket
   ```

   It runs, in order, and stops at the first failure:
   `tofu fmt -check -recursive`, `tofu init -backend=false -lockfile=readonly`, `tofu validate`,
   `tofu test`, an audit of Checkov exceptions, then Checkov 3.3.29 (through `uvx`).
5. Fix what failed. Report the gate output, not a summary of it.

## Checkov findings

- Fix the finding first. Most S3, IAM and logging findings have a one-resource fix.
- If the finding is genuinely the caller's decision (replication, event notifications), skip it
  inline on the resource, with a reason a reviewer can disagree with:

  ```hcl
  resource "aws_s3_bucket" "this" {
    #checkov:skip=CKV_AWS_144:Cross-region replication is configured by callers that need it
  ```

- Never add `soft-fail: true` or a `skip-check:` list to the repository's Checkov config, and
  never pass `--soft-fail` or `--skip-check` on the command line. The gate refuses both config
  settings, and refuses a skip with no reason or a reason under 10 characters.
- Start the repository config from `references/checkov.yaml`.

## Lock file and providers

- Pin providers with `~>` on a minor version in `required_providers`, and commit the lock file.
  The gate runs init with `-lockfile=readonly`, so a provider change must be a deliberate
  `tofu init -upgrade` that a human reviews in the diff.
- For lock hashes on every platform the team uses:
  `tofu providers lock -platform=linux_amd64 -platform=darwin_arm64`.
- Never commit the `.terraform` folder, state files or plan files.

## Root modules: encrypt state

OpenTofu encrypts state and plan files natively. A root module that uses this module should
carry an `encryption` block with `enforced = true` for both state and plan, and take the key
from the environment (a sensitive variable set by `TF_VAR_...`, or a KMS key provider). See
`references/example-root.tf`. Never write the passphrase into a file.

## What the agent does not do

- No `tofu apply`, `destroy`, `import`, `state` subcommands or `-auto-approve`. A person applies.
  Pair this loadout with terraform-plan-only for a hook that enforces it.
- No `tofu plan` against a real account to "check it works": that is what the mocked tests are for.
- No new provider or module source without saying so in the summary.

## Files

- `scripts/gate.sh`: the gate. Env: `TOFU` (default `tofu`), `CHECKOV` (default
  `uvx --from checkov==3.3.29 checkov`).
- `references/main.tf`, `references/variables.tf`, `references/outputs.tf`,
  `references/versions.tf`: a private, versioned, SSE-KMS S3 bucket module with access logging,
  TLS-only policy and noncurrent-version expiry. Checkov: 0 failed, 2 reasoned skips.
- `references/bucket.tftest.hcl`: four `run` blocks with a mocked AWS provider.
- `references/example-root.tf`: root module with enforced state and plan encryption.
- `references/checkov.yaml`: repository Checkov config.
