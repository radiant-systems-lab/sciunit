
from nose.tools import *

from tests import testit


class TestSort(testit.LocalCase):
    def test_all(self):
        pass
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('sort')
        # assert_equal(r.exception.code, 2)
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('sort', '-x')
        # assert_equal(r.exception.code, 2)
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('sort', 'e1')
        # assert_equal(r.exception.code, 1)
        #
        # testit.sciunit('create', 'ok')
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('sort', 'e5', 'e4')
        # assert_equal(r.exception.code, 1)
        #
        # for i in range(1, 6):
        #     testit.sciunit('exec', 'sh', '-c', 'exit %d' % i)
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('sort', 'e3', 'e4', 'e3')
        # assert_equal(r.exception.code, 1)
        #
        # testit.sciunit('rm', 'e2')
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('sort', 'e3', 'e2')
        # assert_equal(r.exception.code, 1)
        #
        # testit.sciunit('sort', 'e4', 'e5')
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e4')
        # assert_equal(r.exception.code, 4)
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e5')
        # assert_equal(r.exception.code, 5)
        #
        # testit.sciunit('sort', 'e5', 'e4', 'e1')
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e1')
        # assert_equal(r.exception.code, 5)
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e2')
        # assert_equal(r.exception.code, 4)
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e3')
        # assert_equal(r.exception.code, 1)
        #
        # with assert_raises(SystemExit) as r:
        #     testit.sciunit('repeat', 'e4')
        # assert_equal(r.exception.code, 3)
