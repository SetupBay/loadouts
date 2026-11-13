#!/usr/bin/env bash
# Feeds sample Bash tool calls to guard-terraform.sh and checks each decision.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
pass=0; failed=0
check() { # want(deny|allow) command
  local want="$1" cmd="$2" out got
  out=$(jq -n --arg c "$cmd" '{tool_name: "Bash", tool_input: {command: $c}}' | bash "$here/guard-terraform.sh")
  if printf '%s' "$out" | grep -q '"permissionDecision": "deny"'; then got=deny; else got=allow; fi
  if [ "$got" = "$want" ]; then pass=$((pass + 1)); else failed=$((failed + 1)); echo "FAIL: wanted $want, got $got: $cmd"; fi
}
check deny  "terraform apply"
check deny  "terraform apply tfplan"
check deny  "cd infra && terraform destroy -target=aws_s3_bucket.logs"
check deny  "tofu apply"
check deny  "terraform plan -out=tfplan && terraform apply -auto-approve tfplan"
check deny  "terraform -chdir=envs/dev apply"
check deny  "terraform import aws_s3_bucket.b my-bucket"
check deny  "terraform state rm aws_instance.web"
check deny  "terraform force-unlock 1234"
check deny  "terraform workspace delete staging"
check deny  "cat terraform.tfstate"
check deny  "TERRAFORM APPLY"
check allow "terraform fmt -recursive"
check allow "terraform validate"
check allow "terraform init -backend=false"
check allow "terraform plan -out=tfplan"
check allow "terraform show -json tfplan > plan.json"
check allow "terraform state list"
check allow "grep -r apply docs/"
check allow "terraform workspace list"
if [ "$failed" -eq 0 ]; then echo "ok: $pass cases"; else echo "failed: $failed of $((pass + failed))"; exit 1; fi
