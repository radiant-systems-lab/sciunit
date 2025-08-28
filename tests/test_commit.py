
from nose.tools import *

from tests import testit


class TestCommit(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('commit', '-x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('commit', 'x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('commit')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')
        testit.sciunit('exec', 'pwd', '-h')

        with assert_raises(SystemExit) as r:
            testit.sciunit('commit')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1', '-P')
        assert_equal(r.exception.code, 0)

        assert_is_none(testit.sciunit('commit'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('commit')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e2')
        assert_equal(r.exception.code, 0)
