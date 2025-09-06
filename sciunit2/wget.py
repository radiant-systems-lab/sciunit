from __future__ import absolute_import

from tqdm import tqdm
import urllib.request
import urllib.error
import tempfile


class TqdmHook(tqdm):
    def update_to(self, b, bsize, tsize):
        self.total = tsize
        self.update(b * bsize - self.n)


class ThrowOnErrorOpener(urllib.request.FancyURLopener):
    def http_error_default(self, url, fp, code, msg, hdrs):
        raise urllib.error.HTTPError(url, code, msg.title(), hdrs, fp)

    http_error_401 = http_error_default
    http_error_407 = http_error_default


def fetch(url, base):
    with tempfile.NamedTemporaryFile(prefix=base, dir='') as fp, \
            TqdmHook(unit='B', unit_scale=True, miniters=1) as t:
        ThrowOnErrorOpener().retrieve(url, fp.name, t.update_to)
        return open(fp.name, 'rb')
