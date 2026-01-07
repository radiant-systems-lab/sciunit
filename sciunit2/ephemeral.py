
import urllib.request
import urllib.error
import requests
from requests.auth import HTTPBasicAuth

from retry import retry
from contextlib import closing
import tempfile
import shutil


def live(fn):
    # this is the API key for the basic plan purchased
    # from file.io at $275/year(before 20% discount).
    # It allows file sizes of
    # up to 10GB with up to 60 requests/minute,
    # 2TB total storage, and 250GB download/month
    # more details here:
    # https://www.file.io/plans
    key = 'WJ4NFWW.K0MKZ61-X9Z4S38-HQBS5QM-D45C0RH'
    auth = HTTPBasicAuth('Authorization', key)
    with open(fn, 'rb') as f:
        with closing(requests.post("https://file.io/?expires=1d", auth=auth,
                                   files={"file": f})) as resp:
            return resp.json()['key'] + '#'


@retry(urllib.error.HTTPError, tries=3, delay=0.3, backoff=2)
def _download(token):
    return urllib.request.urlopen("https://file.io/" + token)


def fetch(token, base):
    with closing(_download(token)) as resp:
        f = tempfile.NamedTemporaryFile(prefix=base, dir='')
        shutil.copyfileobj(resp, f)
        f.seek(0)
        return f
