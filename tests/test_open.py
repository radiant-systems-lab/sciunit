
from nose.tools import *
import os
import threading
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler
from contextlib2 import ExitStack

from tests import testit
import sciunit2.archiver


class TestOpen(testit.LocalCase):
    def test_dir(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('open')
        assert_equal(r.exception.code, 2)

        testit.sciunit('create', 'yes')
        assert_is_none(testit.sciunit('open', 'yes'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', 'a.xml')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', 'nonexistent')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', '-n')
        assert_equal(r.exception.code, 2)

    def test_zip(self):
        testit.sciunit('create', 'yes')

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', 'nonexistent.zip')
        assert_equal(r.exception.code, 1)

        assert_equal(sciunit2.archiver.make('tmp/yes'), 'tmp/yes.zip')

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', 'tmp/yes.zip')
        assert_equal(r.exception.code, 1)

        testit.sciunit('exec', 'true')

        assert_equal(sciunit2.archiver.make('tmp/yes'), 'tmp/yes.zip')
        os.rename('tmp/yes.zip', 'tmp_x.zip')
        testit.sciunit('rm', 'e1')

        try:
            assert_is_none(testit.sciunit('open', './tmp_x.zip'))
        finally:
            os.unlink('tmp_x.zip')

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)

        assert_is_none(testit.sciunit('open', 'yes'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 1)

    def test_rename(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('open', '-m')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', '-m', 'a', 'b')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', '-m', 'nowhere')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'empty')
        testit.sciunit('create', 'old')
        testit.sciunit('exec', 'true')

        assert_is_none(testit.sciunit('open', '-m', 'new'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', 'old')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('repeat', 'e1')
        assert_equal(r.exception.code, 0)

        assert_is_none(testit.sciunit('open', '-m', 'empty'))
        assert_is_none(testit.sciunit('open', '-m', 'notempty'))

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', 'new')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.touch('tmp/new')
            testit.sciunit('open', '-m', 'new')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'empty')

        with assert_raises(SystemExit) as r:
            testit.sciunit('open', '-m', 'notempty')
        assert_equal(r.exception.code, 1)

    def test_url(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('open', 'sftp://localhost/a.zip')
        assert_equal(r.exception.code, 1)

        TCPServer.allow_reuse_address = True
        server = TCPServer(("localhost", 5001), SimpleHTTPRequestHandler)
        started = threading.Event()
        stopped = threading.Event()

        def run():
            started.set()
            while not stopped.is_set():
                server.handle_request()
                stopped.wait(0.01)

        httpd = threading.Thread(target=run)
        httpd.start()

        while not started.is_set():
            started.wait()

        with ExitStack() as st:
            st.callback(httpd.join)
            st.callback(stopped.set)

            testit.sciunit('create', 'a')
            testit.sciunit('exec', 'true')
            testit.sciunit('copy', '-n')

            testit.sciunit('open', 'http://localhost:5001/tmp/a.zip')

            with assert_raises(SystemExit) as r:
                testit.sciunit('repeat', 'e1')
            assert_equal(r.exception.code, 0)

            with assert_raises(SystemExit) as r:
                testit.sciunit('open', 'http://localhost:5001/tmp/b.zip')
            assert_equal(r.exception.code, 1)
