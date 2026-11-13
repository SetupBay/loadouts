variable "name" {
  description = "Bucket name. Globally unique, lower case, 3 to 63 characters."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.name))
    error_message = "name must be 3-63 lower-case letters, digits, dots or hyphens, starting and ending with a letter or digit."
  }
}

variable "kms_key_arn" {
  description = "ARN of the customer-managed KMS key used for default encryption."
  type        = string

  validation {
    condition     = startswith(var.kms_key_arn, "arn:aws:kms:")
    error_message = "kms_key_arn must be a KMS key ARN."
  }
}

variable "log_bucket" {
  description = "Name of the bucket that receives server access logs."
  type        = string
}

variable "noncurrent_days" {
  description = "Days to keep noncurrent object versions before they expire."
  type        = number
  default     = 90

  validation {
    condition     = var.noncurrent_days >= 7 && var.noncurrent_days <= 3650
    error_message = "noncurrent_days must be between 7 and 3650."
  }
}

variable "tags" {
  description = "Tags added to every resource."
  type        = map(string)
  default     = {}
}
