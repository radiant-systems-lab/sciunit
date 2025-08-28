
from nose.tools import *
import os

from unittest.mock import patch
from tests import testit


class TestRemove(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('remove')
        assert_equal(r.exception.code, 2)

        testit.sciunit('create', 'ok')
        assert_true(os.path.isdir('tmp/ok'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('create', 'ok')
        assert_equal(r.exception.code, 1)

    @patch('builtins.input', return_value='Y')
    def test_y(self, inp):
        testit.sciunit('create', 'ok')
        testit.sciunit('remove', 'ok')
        assert_false(os.path.isdir('tmp/ok'))

    @patch('builtins.input', return_value='n')
    def test_n(self, inp):
        testit.sciunit('create', 'ok')
        testit.sciunit('remove', 'ok')
        assert_true(os.path.isdir('tmp/ok'))
