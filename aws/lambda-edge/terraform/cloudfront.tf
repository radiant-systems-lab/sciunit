# Attach Lambda@Edge functions to the existing CloudFront distribution.
#
# The CloudFront distribution was created outside of Terraform.
# Using null_resource + local-exec to safely attach Lambda associations
# without Terraform managing (and potentially overwriting) the full
# CloudFront config.

resource "null_resource" "attach_lambda_edge" {
  # Re-run when Lambda versions change
  triggers = {
    gatekeeper_arn = aws_lambda_function.gatekeeper.qualified_arn
    accounting_arn = aws_lambda_function.accounting.qualified_arn
    distribution   = var.cloudfront_distribution_id
  }

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command     = <<-EOT
      set -euo pipefail

      DIST_ID="${var.cloudfront_distribution_id}"
      PROFILE="${var.aws_profile}"
      GATEKEEPER_ARN="${aws_lambda_function.gatekeeper.qualified_arn}"
      ACCOUNTING_ARN="${aws_lambda_function.accounting.qualified_arn}"

      echo "Fetching current distribution config..."
      aws cloudfront get-distribution-config \
        --id "$DIST_ID" \
        --profile "$PROFILE" > /tmp/cf-dist-config.json

      ETAG=$(python3 -c "import json; print(json.load(open('/tmp/cf-dist-config.json'))['ETag'])")
      echo "ETag: $ETAG"

      python3 << 'PYEOF'
import json, os

gatekeeper_arn = os.environ.get("GATEKEEPER_ARN", "${aws_lambda_function.gatekeeper.qualified_arn}")
accounting_arn = os.environ.get("ACCOUNTING_ARN", "${aws_lambda_function.accounting.qualified_arn}")

with open("/tmp/cf-dist-config.json") as f:
    data = json.load(f)

config = data["DistributionConfig"]
config["DefaultCacheBehavior"]["LambdaFunctionAssociations"] = {
    "Quantity": 2,
    "Items": [
        {
            "LambdaFunctionARN": gatekeeper_arn,
            "EventType": "viewer-request",
            "IncludeBody": False,
        },
        {
            "LambdaFunctionARN": accounting_arn,
            "EventType": "viewer-response",
            "IncludeBody": False,
        },
    ],
}

with open("/tmp/cf-dist-config-updated.json", "w") as f:
    json.dump(config, f, indent=2)
PYEOF

      echo "Updating CloudFront distribution..."
      aws cloudfront update-distribution \
        --id "$DIST_ID" \
        --distribution-config file:///tmp/cf-dist-config-updated.json \
        --if-match "$ETAG" \
        --profile "$PROFILE" > /dev/null

      echo "Lambda@Edge attached to distribution $DIST_ID"
    EOT

    environment = {
      GATEKEEPER_ARN = aws_lambda_function.gatekeeper.qualified_arn
      ACCOUNTING_ARN = aws_lambda_function.accounting.qualified_arn
    }
  }

  depends_on = [
    aws_lambda_function.gatekeeper,
    aws_lambda_function.accounting,
  ]
}
