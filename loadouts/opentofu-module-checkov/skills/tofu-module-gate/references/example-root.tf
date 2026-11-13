# Root module example: calls the bucket module and encrypts state and plan files with
# OpenTofu's built-in state encryption. The passphrase comes from a variable that is
# set in the environment (TF_VAR_state_passphrase), never written to a file.
terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.69"
    }
  }

  encryption {
    key_provider "pbkdf2" "state" {
      passphrase = var.state_passphrase
    }

    method "aes_gcm" "state" {
      keys = key_provider.pbkdf2.state
    }

    state {
      method   = method.aes_gcm.state
      enforced = true
    }

    plan {
      method   = method.aes_gcm.state
      enforced = true
    }
  }
}

variable "state_passphrase" {
  description = "State encryption passphrase, at least 16 characters. Set TF_VAR_state_passphrase."
  type        = string
  sensitive   = true
}

provider "aws" {
  region = "eu-west-2"
}

module "reports" {
  source = "../../modules/s3-bucket"

  name        = "acme-reports-eu"
  kms_key_arn = "arn:aws:kms:eu-west-2:111122223333:key/0d7c2f4e-1111-2222-3333-444455556666"
  log_bucket  = "acme-access-logs"
  tags        = { service = "reports" }
}

output "bucket_arn" {
  value = module.reports.arn
}
