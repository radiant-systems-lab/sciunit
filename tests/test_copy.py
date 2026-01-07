
from nose.tools import *
from unittest import mock
import shutil
from io import StringIO

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

        # Test S3 copy functionality
        # Mock the S3 upload to avoid actual AWS calls during testing
        mock_cf_url = "https://d3okuktvxs1y4w.cloudfront.net/2024-01-07-12:00:00/ok.zip"

        out = StringIO()
        with mock.patch('sys.stdout', out), \
             mock.patch('sciunit2.s3.live', return_value=mock_cf_url):
            testit.sciunit('copy')
        url = out.getvalue().strip()

        # Verify it returns a CloudFront URL
        assert_true(url.startswith('https://d3okuktvxs1y4w.cloudfront.net/'))

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
