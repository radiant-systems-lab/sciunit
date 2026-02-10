# AWS Resources

All resources are in `us-east-1` and managed via Terraform in `aws/lambda-edge/terraform/`.

## Resource Overview

```
                  sciunit copy (upload)
                        │
                        v
              ┌──────────────────┐
              │    S3 Bucket     │
              │ sciunit2-talha   │
              └────────┬─────────┘
                       │ OAC
                       v
              ┌──────────────────┐
              │   CloudFront     │──── viewer-request ──── Gatekeeper Lambda
              │ E2HWZQGHIVF7CP  │                         (checks bandwidth)
              │                  │──── viewer-response ─── Accounting Lambda
              └────────┬─────────┘                         (tracks bytes)
                       │                                        │
                       │                                        v
                       v                               ┌──────────────────┐
                 sciunit open                          │    DynamoDB      │
                  (download)                           │cloudfront_bandwidth│
                                                       └──────────────────┘
```

## Resources

### S3 Bucket — `sciunit2-talha`
- Stores sciunit project archives uploaded via `sciunit copy`
- All public access blocked; only accessible through CloudFront via OAC
- Objects stored under `projects/<timestamp>/<filename>`
- Credentials stored under `persistent/` (not subject to lifecycle rules)

### CloudFront Distribution — `E2HWZQGHIVF7CP`
- Domain: `d3okuktvxs1y4w.cloudfront.net`
- Origin Access Control (OAC): `EZDWNYQO6UZRC` — authenticates CloudFront requests to S3
- Serves downloads for `sciunit open <url>`
- First 1 TB/month of bandwidth is free (vs ~$0.09/GB from S3 direct)
- Created outside Terraform; Lambda associations attached via `null_resource`

### Lambda@Edge — Gatekeeper (`cf-bandwidth-gatekeeper`)
- **Event**: `viewer-request` — runs before CloudFront fetches the object
- **Purpose**: Checks monthly bandwidth usage in DynamoDB; returns HTTP 429 if the 1 TB limit is exceeded
- **Fail-open**: If DynamoDB is unreachable, the request is allowed through
- **Runtime**: Node.js 20.x
- Terraform resource: `aws_lambda_function.gatekeeper`

### Lambda@Edge — Accounting (`cf-bandwidth-accounting`)
- **Event**: `viewer-response` — runs after CloudFront sends the response
- **Purpose**: Reads `Content-Length` (or `Content-Range`) from the response and atomically increments the monthly byte counter in DynamoDB
- **Runtime**: Node.js 20.x
- Terraform resource: `aws_lambda_function.accounting`

### DynamoDB Table — `cloudfront_bandwidth`
- **Billing**: PAY_PER_REQUEST (no provisioned capacity)
- **Schema**: Partition key `pk` (String), attribute `bytes` (Number)
- **Key format**: `sciunit2-talha#YYYY-MM` (e.g., `sciunit2-talha#2026-02`)
- Counter resets naturally each month since the key includes the year-month
- Atomic updates via `UpdateItem ADD` ensure correctness under concurrent requests

### IAM Role — `cloudfront-bandwidth-limiter`
- Trusted by `lambda.amazonaws.com` and `edgelambda.amazonaws.com`
- Permissions: `dynamodb:GetItem`, `dynamodb:UpdateItem` on the bandwidth table, plus CloudWatch Logs

## Bandwidth Limiting

When cumulative downloads for the current month reach 1 TB:
1. Gatekeeper Lambda reads the counter from DynamoDB
2. Returns HTTP 429 with body: "Monthly download bandwidth limit (1 TB) exceeded"
3. The sciunit CLI catches this and displays: "Monthly download bandwidth limit exceeded. Please try again next month or contact the sciunit maintainers."

## Deployment

```bash
# Install Lambda dependencies (required before first deploy)
cd aws/lambda-edge/viewer-request && npm install
cd aws/lambda-edge/viewer-response && npm install

# Deploy/update all resources
cd aws/lambda-edge/terraform
terraform init
terraform apply
```
