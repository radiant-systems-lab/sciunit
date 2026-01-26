"""
AWS credential fetching for sciunit S3 operations.
"""
import requests

# Endpoint that serves the current AWS credentials
CREDENTIALS_URL = "https://d3okuktvxs1y4w.cloudfront.net/persistent/sciunit-aws-creds.json"

def get_aws_credentials():
    """
    Fetches AWS credentials from the endpoint.
    Returns a dict with 'aws_access_key_id' and 'aws_secret_access_key'.
    """
    response = requests.get(CREDENTIALS_URL)
    response.raise_for_status()
    return response.json()
