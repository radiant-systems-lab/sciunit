
from nose.tools import *
import os


from tests import testit


class TestCreate(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('create')
        assert_equal(r.exception.code, 2)

        testit.sciunit('create', 'ok')
        assert_true(os.path.isdir('tmp/ok'))

        testit.sciunit('create', '-f', 'ok')
        assert_true(os.path.isdir('tmp/ok'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('create', 'ok')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('create', 'a.zip')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.touch('tmp/notok')
            testit.sciunit('create', 'notok')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('create', '-h')
        assert_equal(r.exception.code, 2)
