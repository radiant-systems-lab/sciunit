
from sciunit2.sharing import AbstractService, NotAuthorized, NotFound

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import hs_restclient
import os
from contextlib2 import suppress

CLIENT_ID = r'vG5R4zZFO6uJZBj3m0DWtUK6Va44jTQ4KoqtaLpn'
CLIENT_SECRET = (
    r'vSe21nHklEq6jrZ3Z4QsiNN9LxG7FWHoL8w0UvuWBLUEoZLh1QwRVBYiN2iu8GMQ'
    r'8aHar4WyfefvyZrUI3JZ23LkiErv1wz1U38GgAMKtikB095DVo8nkh0dLoiubHvE')

AUTH_URL = 'https://www.hydroshare.org/o/authorize/'
TOKN_URL = 'https://www.hydroshare.org/o/token/'
CBCK_URL = 'https://sciunit.run/cb'


class Unauthenticated(Exception):
    pass


class HydroShare(AbstractService):
    __slots__ = ['__t', '__w', '__h']

    name = 'hydroshare'

    def __init__(self, tokenp, wizard):
        self.__t = tokenp
        self.__w = wizard
        self.__h = None

    def __prepare_handle(self):
        if self.__h is None:
            self.__assign_handle()

    def __assign_handle(self):
        try:
            self.__h = hs_restclient.HydroShare(
                auth=hs_restclient.HydroShareAuthOAuth2(
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    token=self.__t.get()))
        except KeyError:
            raise Unauthenticated

    def __authenticated(f):
        def inner(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Unauthenticated:
                oauth2 = OAuth2Session(CLIENT_ID, redirect_uri=CBCK_URL)
                authorization_url, state = oauth2.authorization_url(AUTH_URL)
                self.__w.info(
                    'Please go to the following link and authorize access:\n'
                    '\n'
                    '%s\n', authorization_url)
                code = self.__w.prompt('Paste the authorization code:')
                token = oauth2.fetch_token(TOKN_URL,
                                           code=code,
                                           client_secret=CLIENT_SECRET)
                self.__t.reset(token)
                self.__assign_handle()
                self.__h.session = oauth2
                return f(self, *args, **kwargs)
        return inner

    def __refreshed(f):
        def inner(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except TokenExpiredError:
                token = self.__h.session.refresh_token(
                    TOKN_URL,
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET)
                self.__t.reset(token)
                return f(self, *args, **kwargs)
            except hs_restclient.HydroShareNotAuthorized as exc:
                raise NotAuthorized(exc)
            except hs_restclient.HydroShareNotFound as exc:
                raise NotFound(exc)
        return inner

    @__authenticated
    def __login(self):
        self.__prepare_handle()
        u = self.__get_user()
        if 'username' not in u:
            raise Unauthenticated
        self.__w.info(
            u'Logged in as "{0[last_name]}, {0[first_name]} <{0[email]}>"'
            .format(u))

    @__refreshed
    def __get_user(self):
        return self.__h.getUserInfo()

    @__refreshed
    def __get_title(self, article):
        return self.__h.getSystemMetadata(article.id)[u'resource_title']

    @__refreshed
    def __create_new_version(self, article):
        resp = self.__h.resource(article.id).version()
        resp.raise_for_status()
        return resp.text

    @__refreshed
    def __create_new_resource(self, title):
        return self.__h.createResource(resource_type='GenericResource',
                                       title=title or 'Untitled')

    @__refreshed
    def __upload_file(self, article, fn):
        with suppress(hs_restclient.HydroShareNotFound):
            self.__h.deleteResourceFile(article.id, os.path.basename(fn))
        with self.__w.progress(article.codename, os.path.getsize(fn)) as p:
            def cb(monitor):
                p.update(monitor.bytes_read - p.n)
            self.__h.addResourceFile(article.id, fn, progress_callback=cb)

    def __try_setup(self, article):
        with suppress(NotFound):
            title = self.__get_title(article)
            if self.__w.ask(
                    u'Create a new version of the article "%s"?', title):
                article.id = self.__create_new_version(article)
                return

        title = self.__w.prompt('Title for the new article:')
        article.id = self.__create_new_resource(title)

    def setup(self, article):
        self.__login()
        self.__try_setup(article)

    def push(self, article, fn):
        self.__prepare_handle()
        self.__upload_file(article, fn)
