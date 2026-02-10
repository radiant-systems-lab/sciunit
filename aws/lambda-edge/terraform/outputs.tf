output "dynamodb_table_name" {
  description = "DynamoDB table for bandwidth tracking"
  value       = aws_dynamodb_table.cloudfront_bandwidth.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.cloudfront_bandwidth.arn
}

output "iam_role_arn" {
  description = "IAM role ARN for Lambda@Edge functions"
  value       = aws_iam_role.lambda_edge.arn
}

output "gatekeeper_qualified_arn" {
  description = "Published version ARN of the gatekeeper Lambda (viewer-request)"
  value       = aws_lambda_function.gatekeeper.qualified_arn
}

output "accounting_qualified_arn" {
  description = "Published version ARN of the accounting Lambda (viewer-response)"
  value       = aws_lambda_function.accounting.qualified_arn
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID with Lambda@Edge attached"
  value       = var.cloudfront_distribution_id
}
