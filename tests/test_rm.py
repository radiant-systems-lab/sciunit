
from nose.tools import *

from tests import testit


class TestRm(testit.LocalCase):
    def test_single(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('rm')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', '-x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', 'e1')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')
        assert_is_none(testit.sciunit('rm', 'e1'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', 'e0')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', 'wat')
        assert_equal(r.exception.code, 1)

        testit.sciunit('exec', 'pwd')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)

        assert_is_none(testit.sciunit('rm', 'e1'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 1)

        assert_is_none(testit.sciunit('exec', 'true'))

    def test_range(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', 'e1-')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')

        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', 'e0-1')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', 'e1-0')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('rm', 'e-3')
        assert_equal(r.exception.code, 1)

        for _ in range(6):
            testit.sciunit('exec', 'true')

        testit.sciunit('rm', 'e5-4')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e5')
        assert_equal(r.exception.code, 0)

        testit.sciunit('rm', 'e4-5')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e5')
        assert_equal(r.exception.code, 1)

        testit.sciunit('rm', 'e3-5')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e3')
        assert_equal(r.exception.code, 1)

        testit.sciunit('rm', 'e5-')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e6')
        assert_equal(r.exception.code, 1)

        testit.sciunit('rm', 'e2-2')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e2')
        assert_equal(r.exception.code, 1)

        testit.sciunit('rm', 'e1-10')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 1)

        assert_is_none(testit.sciunit('rm', 'e1-10'))
        assert_is_none(testit.sciunit('exec', 'true'))
