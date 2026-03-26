
from nose.tools import *
from unittest import mock
import shutil
from io import StringIO
from sciunit2.s3 import CF_DOMAIN

from tests import testit


class TestCopy(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('copy', '-x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('copy', 'x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('copy')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')
        testit.sciunit('exec', 'pwd')

        with assert_raises(SystemExit) as r, mock.patch('time.sleep', id):
            testit.sciunit('open', 'nonexistent#')
        assert_equal(r.exception.code, 1)

        # Test S3 copy functionality (actual upload and download)
        out = StringIO()
        with mock.patch('sys.stdout', out):
            testit.sciunit('copy')
        cf_url = out.getvalue().strip()

        # Verify it returns a CloudFront URL
        assert_true(cf_url.startswith(CF_DOMAIN))

        # Open the sciunit from CloudFront URL (actual download)
        assert_is_none(testit.sciunit('open', cf_url))

        # Verify we can repeat from the downloaded sciunit
        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)

        # Test local copy with -n flag
        out = StringIO()
        with mock.patch('sys.stdout', out):
            testit.sciunit('copy', '-n')
        path = out.getvalue().strip()

        assert_true(path.endswith('.zip'))
        assert_is_none(testit.sciunit('open', path))

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)
