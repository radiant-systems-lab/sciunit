
from nose.tools import *
import os
import io
from unittest import mock
import ddt
import pwd
import re

from tests import testit
from contextlib import redirect_stdout


@ddt.ddt
class TestGiven(testit.LocalCase):
    @ddt.data('/usr/local/bash', '/bin/tcsh', '/opt/bin/fish')
    def test_all(self, shell):
        def mock_getpwuid(uid):
            return pwd.struct_passwd(['', '', '', '', '', '', shell])

        testit.mkdir('tmp')

        patch_tilde = mock.patch('os.path.expanduser',
                                 lambda x: x.replace('~/', 'tmp/'))
        with mock.patch('pwd.getpwuid', mock_getpwuid):
            patch_tilde.start()
            with assert_raises(SystemExit) as r:
                testit.sciunit('post-install', '-x')
            assert_equal(r.exception.code, 2)

            with redirect_stdout(io.StringIO()) as out:
                testit.sciunit('post-install')

            if not out.getvalue():
                patch_tilde.stop()
                return

            assert_true(out.getvalue().startswith('x '))
            # 'p' points to file .bash_completion
            p = os.path.expanduser(out.getvalue().rstrip()[2:])
            assert_true(os.path.isfile(p))

            with open(p) as fp:
                content = fp.read()

            with redirect_stdout(io.StringIO()) as out:
                testit.sciunit('post-install')

            with open(p) as fp:
                assert_equal(fp.read(), content)

            a = 'echo "old code"\n'
            b = 'more code\n'
            with open(p, 'w') as fp:
                fp.write(a)
                fp.write(content)
                fp.write(b)

            with redirect_stdout(io.StringIO()) as out:
                testit.sciunit('post-install')

            with open(p) as fp:
                assert_equal(fp.read(), a + content + b)

            os.unlink(p)
            os.mkdir(p)

            with redirect_stdout(io.StringIO()) as out:
                testit.sciunit('post-install')

            patch_tilde.stop()
            po = re.search(r'^\s*(~?/[^\n]*)$', out.getvalue(), re.M).group(1)
            assert_true(os.path.isfile(os.path.expanduser(po)))
