from __future__ import absolute_import

from nose.tools import *
import os
import testpath

from tests import testit


class TestRepeat(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', '-i')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'ok')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'asdf')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 1)

        testit.sciunit('exec', 'pwd')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)

        testit.sciunit('create', 'ok2')
        testit.sciunit('exec', 'sh', '-c', 'exit 3')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 3)

        testit.sciunit('open', 'ok')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1', '-x')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1', '-L', '-P')
        assert_equal(r.exception.code, 0)

        testit.sciunit('open', 'ok')
        with testpath.modified_env({'SHELL': '/bin/true'}):
            assert_is_none(testit.sciunit('exec', '-i'))

        assert_true(not os.path.exists('tmp/ok/e2'))
        assert_true(os.path.exists('tmp/ok/e1'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e2')
        assert_equal(r.exception.code, 0)

        assert_true(os.path.exists('tmp/ok/e2'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e2', '-l')
        assert_equal(r.exception.code, 1)

        assert_true(not os.path.exists('tmp/ok/e3'))
       
        assert_is_none(testit.sciunit('commit'))
        
        assert_true(not os.path.exists('tmp/ok/e3'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e3')
        assert_equal(r.exception.code, 0)
        assert_true(os.path.exists('tmp/ok/e3'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1', '-L')
        assert_equal(r.exception.code, 0)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)

        os.unlink('tmp/ok/e2.json')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e2')
        assert_equal(r.exception.code, 1)
