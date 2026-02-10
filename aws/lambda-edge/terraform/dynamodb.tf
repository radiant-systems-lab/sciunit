resource "aws_dynamodb_table" "cloudfront_bandwidth" {
  name         = "cloudfront_bandwidth"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"

  attribute {
    name = "pk"
    type = "S"
  }

  tags = {
    Project = "sciunit"
    Purpose = "CloudFront bandwidth tracking"
  }
}
