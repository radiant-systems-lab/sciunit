
from nose.tools import *

from tests import testit


class TestList(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('list', '-x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('list', 'x')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('list')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')
        assert_is_none(testit.sciunit('list'))

        testit.sciunit('exec', 'pwd')
        assert_is_none(testit.sciunit('list'))
