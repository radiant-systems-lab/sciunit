
from nose.tools import *
from tqdm import tqdm
import requests_mock
import os

from sciunit2.sharing import AbstractWizard
from sciunit2.config import Config
from sciunit2.credentials import TokenPtr
from sciunit2.sharing.hydroshare import HydroShare
from sciunit2.sharing.article import Article


class FaultyWizard(AbstractWizard):
    def ask(self, msg, *args):
        return True

    def prompt(self, msg, *args):
        return ''

    def info(self, msg, *args):
        pass

    def progress(self, msg, nbytes):
        return tqdm(disable=True)


@requests_mock.mock()
def test_happy(m):
    m.get('/hsapi/userInfo/',
          json={
              "username": "username",
              "first_name": "First",
              "last_name": "Last",
              "email": "user@domain.com"
          })
    m.get('/hsapi/resource/types',
          json=[
              {"resource_type": "GenericResource"},
              {"resource_type": "CompositeResource"},
          ])
    m.post('/hsapi/resource/',
           status_code=201,
           json={
               "resource_type": "GenericResource",
               "resource_id": "511debf8858a4ea081f78d66870da76c"
           })
    m.get('/hsapi/resource/511debf8858a4ea081f78d66870da76c/sysmeta/',
          json={
              "resource_type": "GenericResource",
              "resource_title": "Untitled",
              "resource_id": "511debf8858a4ea081f78d66870da76c",
          })
    m.post('/hsapi/resource/511debf8858a4ea081f78d66870da76c/version/',
           status_code=202,
           text='6dbb0dfb8f3a498881e4de428cb1587c')
    m.delete('/hsapi/resource/511debf8858a4ea081f78d66870da76c/files/'
             'test_hydroshare.py',
             status_code=404)
    m.delete('/hsapi/resource/6dbb0dfb8f3a498881e4de428cb1587c/files/'
             'test_hydroshare.py',
             json={"resource_id": "6dbb0dfb8f3a498881e4de428cb1587c"})
    m.post('/hsapi/resource/511debf8858a4ea081f78d66870da76c/files/',
           status_code=201,
           json={"resource_id": "511debf8858a4ea081f78d66870da76c"})

    def upload_cb(request, context):
        request.text.read()
        return {"resource_id": "6dbb0dfb8f3a498881e4de428cb1587c"}
    m.post('/hsapi/resource/6dbb0dfb8f3a498881e4de428cb1587c/files/',
           status_code=201,
           json=upload_cb)

    cred = TokenPtr('hs', Config(unrepr=True))
    cred.reset({'access_token': 'sth', 'expires_in': 60})
    srv = HydroShare(cred, FaultyWizard())
    article = Article('x', Config())
    fn = os.path.join(os.path.dirname(__file__), 'test_hydroshare.py')
    srv.setup(article)
    srv.push(article, fn)

    srv.setup(article)
    srv.push(article, fn)


def test_unhappy():
    cred = TokenPtr('hs', Config(unrepr=True))
    srv = HydroShare(cred, FaultyWizard())
    with assert_raises(Exception):
        srv.setup('x')
