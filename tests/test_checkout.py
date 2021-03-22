from __future__ import absolute_import

from nose.tools import *
import os
import testpath

from tests import testit


class TestCheckout(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('checkout')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('checkout', '-i')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('checkout', 'e1')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')

        with assert_raises(SystemExit) as r:
            testit.sciunit('checkout', 'asdf')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('checkout', 'e1')
        assert_equal(r.exception.code, 1)

        testit.sciunit('exec', 'pwd')
        testit.sciunit('checkout', 'e1')
        assert_true(os.path.isdir('tmp/ok/cde-package'))
