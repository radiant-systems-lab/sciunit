
from nose.tools import *

from tests import testit


class TestShow(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('show', '-x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('show')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')

        with assert_raises(SystemExit) as r:
            testit.sciunit('show')
        assert_equal(r.exception.code, 2)

        testit.sciunit('exec', 'pwd')
        with assert_raises(SystemExit) as r:
            testit.sciunit('show')
        assert_equal(r.exception.code, 2)

        testit.sciunit('exec', 'true')
        assert_is_none(testit.sciunit('show', 'e1'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('show', 'e1', 'e2')
        assert_equal(r.exception.code, 2)

        testit.sciunit('rm', 'e1')
        assert_is_none(testit.sciunit('show', 'e2'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('show', 'e1')
        assert_equal(r.exception.code, 1)

        testit.sciunit('rm', 'e2')

        with assert_raises(SystemExit) as r:
            testit.sciunit('show')
        assert_equal(r.exception.code, 2)
