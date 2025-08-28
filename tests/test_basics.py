
from nose.tools import *

from tests import testit


class TestBasics(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit()
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('-h')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('nonexistent')
        assert_equal(r.exception.code, 2)

        assert_is_none(testit.sciunit('--help'))
        assert_is_none(testit.sciunit('--version'))
