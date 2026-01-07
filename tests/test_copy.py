
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

        # these test cases need revision because copy functionality
        # is depdendent on file.io which
        # has been changed to limewire. We need a new service.
        # out = StringIO()
        # with mock.patch('sys.stdout', out):
        #     testit.sciunit('copy')
        # token = out.getvalue().strip()
        #
        # # this case fails due to ssl handshake error
        # # shutil.rmtree('tmp', True)
        # # assert_is_none(testit.sciunit('open', token))
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e1')
        # assert_equal(r.exception.code, 0)
        #
        # out = StringIO()
        # with mock.patch('sys.stdout', out):
        #     testit.sciunit('copy', '-n')
        # path = out.getvalue().strip()
        #
        # assert_true(path.endswith('.zip'))
        # assert_is_none(testit.sciunit('open', path))
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e1')
        # assert_equal(r.exception.code, 0)
