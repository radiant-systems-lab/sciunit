import boto3
import tempfile
import shutil
import os
from datetime import datetime
from retry import retry
import urllib



CF_DOMAIN  = "https://d3okuktvxs1y4w.cloudfront.net"

def live(fn, bucket="sciunit2-talha"):
    """
    Uploads a file to S3 and returns a CF download URL.
    """
    s3 = boto3.client('s3')
    key = datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + "/" + fn
    s3.upload_file(fn, bucket, key)
    cf_url = f"{CF_DOMAIN}/{key}"
    return cf_url
    
@retry(urllib.error.HTTPError, tries=3, delay=0.3, backoff=2)
def fetch(url, base):
    """
    Downloads a file from a CF URL and returns a file-like object.
    """
    import requests
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        f = tempfile.NamedTemporaryFile(prefix=base, dir="")
        shutil.copyfileobj(resp.raw, f)
        f.seek(0)
        return f