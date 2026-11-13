# Runs with `tofu test`: a mocked AWS provider, so no credentials, no API calls, nothing created.
mock_provider "aws" {
  mock_data "aws_iam_policy_document" {
    defaults = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
    }
  }
}

variables {
  name        = "acme-reports-eu"
  kms_key_arn = "arn:aws:kms:eu-west-2:111122223333:key/0d7c2f4e-1111-2222-3333-444455556666"
  log_bucket  = "acme-access-logs"
}

run "secure_defaults" {
  command = plan

  assert {
    condition     = aws_s3_bucket_versioning.this.versioning_configuration[0].status == "Enabled"
    error_message = "Versioning must be enabled."
  }

  assert {
    condition = alltrue([
      aws_s3_bucket_public_access_block.this.block_public_acls,
      aws_s3_bucket_public_access_block.this.block_public_policy,
      aws_s3_bucket_public_access_block.this.ignore_public_acls,
      aws_s3_bucket_public_access_block.this.restrict_public_buckets,
    ])
    error_message = "All four public access block settings must be true."
  }

  assert {
    condition     = one([for r in aws_s3_bucket_server_side_encryption_configuration.this.rule : one(r.apply_server_side_encryption_by_default).sse_algorithm]) == "aws:kms"
    error_message = "Default encryption must be SSE-KMS."
  }

  assert {
    condition     = aws_s3_bucket_ownership_controls.this.rule[0].object_ownership == "BucketOwnerEnforced"
    error_message = "ACLs must be disabled (BucketOwnerEnforced)."
  }

  assert {
    condition     = aws_s3_bucket_logging.this.target_prefix == "s3/acme-reports-eu/"
    error_message = "Access logs must go under s3/<name>/."
  }
}

run "rejects_bad_name" {
  command = plan

  variables {
    name = "Acme_Reports"
  }

  expect_failures = [var.name]
}

run "rejects_non_kms_key" {
  command = plan

  variables {
    kms_key_arn = "alias/aws/s3"
  }

  expect_failures = [var.kms_key_arn]
}

run "rejects_short_retention" {
  command = plan

  variables {
    noncurrent_days = 1
  }

  expect_failures = [var.noncurrent_days]
}
