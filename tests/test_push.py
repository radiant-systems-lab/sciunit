
from nose.tools import *
from tqdm import tqdm
import requests_mock
from unittest import mock
from freezegun import freeze_time
from datetime import timedelta

from sciunit2.sharing import AbstractWizard

from tests import testit


class NonEmptyWizard(AbstractWizard):
    def ask(self, msg, *args):
        return False

    def prompt(self, msg, *args):
        return 'sometoken'

    def info(self, msg, *args):
        pass

    def progress(self, msg, nbytes):
        return tqdm(disable=True)


class TestPush(testit.LocalCase):
    def test_cli(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit('push', '--setup')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('push', 'x', 'y')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('push', 'x', 'y', '--setup', 'hs')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('push', '--file')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('push', '--file', 'x', '--setup', 'hs')
        assert_equal(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('push', 'x', '--setup', 'hs')
        assert_equal(r.exception.code, 1)

        testit.sciunit('create', 'yes')

        with assert_raises(SystemExit) as r:
            testit.sciunit('push', 'x', '--setup', 'nonexistent')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('push')
        assert_equal(r.exception.code, 1)

        with assert_raises(SystemExit) as r:
            testit.sciunit('push', 'x')
        assert_equal(r.exception.code, 1)

        class CancellingWizard(NonEmptyWizard):
            def prompt(self, msg, *args):
                raise EOFError

        with mock.patch('sciunit2.command.push.TerminalWizard',
                        CancellingWizard):
            assert_is_none(testit.sciunit('push', 'x', '--setup', 'hs'))

    @requests_mock.mock()
    def test_flow(self, m):
        m.post('/o/token/',
               json={
                   "access_token": "2YotnFZFEjr1zCsicMWpAA",
                   "expires_in": 60,
               })
        passes = {
            "username": "username",
            "first_name": "First",
            "last_name": "Last",
            "email": "user@domain.com"
        }
        m.get('/hsapi/userInfo/',
              [
                  {'json': passes},
                  {'json': {"organization": "None", "title": "None"}},
                  {'json': passes},
              ])
        m.get('/hsapi/resource/types',
              json=[{"resource_type": "GenericResource"}])
        m.post('/hsapi/resource/',
               status_code=201,
               json={
                   "resource_type": "GenericResource",
                   "resource_id": "511debf8858a4ea081f78d66870da76c"
               })
        m.get('/hsapi/resource/511debf8858a4ea081f78d66870da76c/sysmeta/',
              json={
                  "resource_type": "GenericResource",
                  "resource_title": "sometoken",
                  "resource_id": "511debf8858a4ea081f78d66870da76c",
              })
        m.delete('/hsapi/resource/511debf8858a4ea081f78d66870da76c/files/'
                 'yes.zip',
                 status_code=404)
        m.delete('/hsapi/resource/511debf8858a4ea081f78d66870da76c/files/'
                 'setup.py',
                 status_code=404)
        m.post('/hsapi/resource/511debf8858a4ea081f78d66870da76c/files/',
               status_code=201,
               json={"resource_id": "511debf8858a4ea081f78d66870da76c"})

        testit.sciunit('create', 'yes')

        testit.touch('tmp/setup.py')
        with mock.patch('sciunit2.command.push.TerminalWizard',
                        NonEmptyWizard):
            testit.sciunit('push', 'x', '--setup', 'hs')
            testit.sciunit('push')
            testit.sciunit('push', 'x', '--setup', 'hydroshare')
            testit.sciunit('push', '--file', 'tmp/setup.py')

            with freeze_time() as clock:
                clock.tick(timedelta(seconds=60))
                testit.sciunit('push')

            m.get('/hsapi/resource/511debf8858a4ea081f78d66870da76c/sysmeta/',
                  status_code=403)
            m.post('/hsapi/resource/511debf8858a4ea081f78d66870da76c/files/',
                   status_code=404)

            with assert_raises(SystemExit) as r:
                testit.sciunit('push', 'x', '--setup', 'HS')
            assert_equal(r.exception.code, 1)

            with assert_raises(SystemExit) as r:
                testit.sciunit('push', 'x')
            assert_equal(r.exception.code, 1)
