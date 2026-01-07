
from sciunit2.exceptions import CommandError
from sciunit2.sharing import NotFound
from sciunit2.config import Config

import os


def of(path, codename):
    return Article(codename, Config(os.path.join(path, 'config')))


def most_recent(path):
    try:
        with open(os.path.join(path, '.most_recent')) as f:
            ln = f.readline()
            assert ln.endswith('\n')
            article = of(path, ln[:-1])
            article.id
            return article

    except (NotFound, IOError):
        raise CommandError('no recently pushed article')


def save_recent(path, article):
    with open(os.path.join(path, '.most_recent'), 'w') as f:
        print(article.codename, file=f)


class Article(object):
    __slots__ = ['__cfg', '__sect', '__cn']

    def __init__(self, codename, cfg):
        self.__cfg = cfg
        self.__sect = cfg.section('article', codename)
        self.__cn = codename

    def __wrapped(f):
        def inner(self):
            try:
                return f(self)
            except KeyError:
                raise NotFound('article %r is not configured' % self.codename)
        return inner

    @property
    def codename(self):
        return self.__cn

    @property
    @__wrapped
    def id(self):
        return self.__sect['id']

    @id.setter
    def id(self, newid):
        self.__sect['id'] = newid
        self.__cfg.write()

    @property
    @__wrapped
    def service(self):
        return self.__sect['service']

    @service.setter
    def service(self, srv):
        self.__sect['service'] = srv
