// Viewer-Request Lambda@Edge — Gatekeeper
// Checks monthly bandwidth usage and blocks downloads if 1 TB is exceeded.

import { DynamoDBClient, GetItemCommand } from "@aws-sdk/client-dynamodb";

const BUCKET_NAME = "sciunit2-talha";
const LIMIT_BYTES = 1_000_000_000_000; // 1 TB (decimal)

// Lambda@Edge runs at edge locations — DynamoDB is in us-east-1
const ddb = new DynamoDBClient({ region: "us-east-1" });

export async function handler(event) {
  const request = event.Records[0].cf.request;

  try {
    // Compute current month key: "sciunit2-talha#2026-02"
    const now = new Date();
    const month = `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, "0")}`;
    const pk = `${BUCKET_NAME}#${month}`;

    const result = await ddb.send(
      new GetItemCommand({
        TableName: "cloudfront_bandwidth",
        Key: { pk: { S: pk } },
        ProjectionExpression: "bytes",
      })
    );

    const usedBytes = result.Item?.bytes?.N ? Number(result.Item.bytes.N) : 0;

    if (usedBytes >= LIMIT_BYTES) {
      // Monthly limit exceeded — return 429 Too Many Requests
      return {
        status: "429",
        statusDescription: "Too Many Requests",
        headers: {
          "content-type": [{ key: "Content-Type", value: "text/plain" }],
          "retry-after": [{ key: "Retry-After", value: "86400" }],
        },
        body: "Monthly download bandwidth limit (1 TB) exceeded. Try again next month.",
      };
    }
  } catch (err) {
    // Fail-open: if DynamoDB is unreachable, allow the request through
    console.error("Gatekeeper error (fail-open):", err);
  }

  // Allow the request
  return request;
}
