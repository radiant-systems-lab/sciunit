// Viewer-Response Lambda@Edge — Accounting
// Tracks bytes served by atomically incrementing the monthly counter in DynamoDB.

import { DynamoDBClient, UpdateItemCommand } from "@aws-sdk/client-dynamodb";

const BUCKET_NAME = "sciunit2-talha";

// Lambda@Edge runs at edge locations — DynamoDB is in us-east-1
const ddb = new DynamoDBClient({ region: "us-east-1" });

export async function handler(event) {
  const response = event.Records[0].cf.response;

  // Only count successful responses (2xx)
  const status = parseInt(response.status, 10);
  if (status < 200 || status >= 300) {
    return response;
  }

  try {
    const headers = response.headers;
    let bytesServed = 0;

    // For range/resumed downloads, use Content-Range to get actual bytes served
    // Format: "bytes 0-999/5000" → served 1000 bytes
    if (headers["content-range"]?.[0]?.value) {
      const match = headers["content-range"][0].value.match(/bytes\s+(\d+)-(\d+)/);
      if (match) {
        bytesServed = parseInt(match[2], 10) - parseInt(match[1], 10) + 1;
      }
    } else if (headers["content-length"]?.[0]?.value) {
      // Full response — use Content-Length
      bytesServed = parseInt(headers["content-length"][0].value, 10);
    }

    if (bytesServed > 0) {
      // Compute current month key
      const now = new Date();
      const month = `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, "0")}`;
      const pk = `${BUCKET_NAME}#${month}`;

      // Atomically increment the byte counter
      await ddb.send(
        new UpdateItemCommand({
          TableName: "cloudfront_bandwidth",
          Key: { pk: { S: pk } },
          UpdateExpression: "ADD bytes :b",
          ExpressionAttributeValues: {
            ":b": { N: String(bytesServed) },
          },
        })
      );
    }
  } catch (err) {
    // Fail-open: don't block the response if accounting fails
    console.error("Accounting error:", err);
  }

  return response;
}
