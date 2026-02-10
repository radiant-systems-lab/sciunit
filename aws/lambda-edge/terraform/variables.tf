variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "talha-temp"
}

variable "bucket_name" {
  description = "S3 bucket name used as DynamoDB partition key prefix"
  type        = string
  default     = "sciunit2-talha"
}

variable "cloudfront_distribution_id" {
  description = "ID of the existing CloudFront distribution to attach Lambda@Edge to"
  type        = string
}

variable "bandwidth_limit_bytes" {
  description = "Monthly bandwidth limit in bytes (1 TB = 1000000000000)"
  type        = number
  default     = 1000000000000
}
