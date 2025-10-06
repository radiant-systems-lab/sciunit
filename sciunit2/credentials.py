
from sciunit2.config import Config
import sciunit2.workspace


def for_(srvname):
    return TokenPtr(srvname,
                    Config(sciunit2.workspace.location_for('config'),
                           unrepr=True))


class TokenPtr(object):
    __slots__ = ['__cfg', '__key']

    def __init__(self, key, cfg):
        self.__cfg = cfg
        self.__key = key

    def get(self):
        return self.__cfg[self.__key].dict()

    def reset(self, token):
        self.__cfg[self.__key] = token
        self.__cfg.write()
