# S3 Integration for Sciunit Copy

## Overview

Sciunit uses AWS S3 for storing and sharing sciunit packages via the `sciunit copy` command. This enables users to easily share their reproducible research containers across machines and with collaborators.

## Architecture

```
┌─────────────┐     upload      ┌─────────────┐
│   sciunit   │ ───────────────>│   AWS S3    │
│    copy     │                 │   Bucket    │
└─────────────┘                 └──────┬──────┘
                                       │
                                       │ origin
                                       v
┌─────────────┐    download     ┌─────────────┐
│   sciunit   │ <───────────────│ CloudFront  │
│    open     │                 │    CDN      │
└─────────────┘                 └─────────────┘
```

## How It Works

### Upload (`sciunit copy`)
1. Creates a ZIP archive of the current sciunit
2. Fetches AWS credentials from a public endpoint
3. Uploads the archive to S3 bucket
4. Returns a CloudFront URL for downloading

### Download (`sciunit open <url>`)
1. Downloads the sciunit archive via CloudFront CDN
2. Extracts and opens the sciunit locally

## Why CloudFront?

We use CloudFront as a CDN layer on top of S3 for downloads because:

| Feature | S3 Direct | CloudFront |
|---------|-----------|------------|
| First 1TB/month bandwidth | Paid (~$0.09/GB) | **Free** |
| Global edge locations | No | Yes |
| Caching | No | Yes |
| HTTPS | Yes | Yes |

**Cost savings**: CloudFront offers 1TB of free data transfer per month, making it ideal for distributing sciunit packages without incurring bandwidth costs.

## Configuration

- **S3 Bucket**: `sciunit2-talha`
- **CloudFront Domain**: `https://d3okuktvxs1y4w.cloudfront.net`
- **Credentials Endpoint**: Fetched dynamically to support rotation

## Usage

```bash
# Upload a sciunit to S3 and get a shareable URL
sciunit copy
# Output: https://d3okuktvxs1y4w.cloudfront.net/projects/2024-01-07-12:00:00/myproject.zip

# Open a sciunit from the URL
sciunit open https://d3okuktvxs1y4w.cloudfront.net/projects/2024-01-07-12:00:00/myproject.zip

# Local copy only (no S3 upload)
sciunit copy -n
```

## Security

- AWS credentials are stored securely and fetched at runtime
- Credentials have limited permissions (S3 read/write only)
- Credentials are rotated periodically
