# --- Zip archives from existing Lambda source files ---

data "archive_file" "viewer_request" {
  type        = "zip"
  source_dir  = "${path.module}/../viewer-request"
  excludes    = ["package.json", "package-lock.json"]
  output_path = "${path.module}/dist/viewer-request.zip"
}

data "archive_file" "viewer_response" {
  type        = "zip"
  source_dir  = "${path.module}/../viewer-response"
  excludes    = ["package.json", "package-lock.json"]
  output_path = "${path.module}/dist/viewer-response.zip"
}

# --- Gatekeeper: blocks requests when monthly bandwidth >= 1 TB ---

resource "aws_lambda_function" "gatekeeper" {
  function_name    = "cf-bandwidth-gatekeeper"
  description      = "CloudFront viewer-request: blocks downloads when monthly bandwidth limit is exceeded"
  runtime          = "nodejs20.x"
  handler          = "index.handler"
  role             = aws_iam_role.lambda_edge.arn
  filename         = data.archive_file.viewer_request.output_path
  source_code_hash = data.archive_file.viewer_request.output_base64sha256
  timeout          = 5
  memory_size      = 128
  publish          = true # Lambda@Edge requires a published version

  tags = {
    Project = "sciunit"
  }
}

# --- Accounting: tracks bytes served in DynamoDB ---

resource "aws_lambda_function" "accounting" {
  function_name    = "cf-bandwidth-accounting"
  description      = "CloudFront viewer-response: tracks bytes served for monthly bandwidth accounting"
  runtime          = "nodejs20.x"
  handler          = "index.handler"
  role             = aws_iam_role.lambda_edge.arn
  filename         = data.archive_file.viewer_response.output_path
  source_code_hash = data.archive_file.viewer_response.output_base64sha256
  timeout          = 5
  memory_size      = 128
  publish          = true # Lambda@Edge requires a published version

  tags = {
    Project = "sciunit"
  }
}
