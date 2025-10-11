
import abc
from abc import abstractmethod, abstractproperty


class NotAuthorized(Exception):
    pass


class NotFound(Exception):
    pass


class AbstractWizard:
    __metaclass__ = abc.ABCMeta

    @abstractmethod
    def ask(self, msg, *args):
        raise NotImplementedError

    @abstractmethod
    def prompt(self, msg, *args):
        raise NotImplementedError

    @abstractmethod
    def info(self, msg, *args):
        raise NotImplementedError

    @abstractmethod
    def progress(self, msg, nbytes):
        raise NotImplementedError


class AbstractService:
    __metaclass__ = abc.ABCMeta

    name = NotImplemented

    @abstractmethod
    def __init__(self, tokenp, wizard):
        raise NotImplementedError

    @abstractmethod
    def setup(self, article):
        raise NotImplementedError

    @abstractmethod
    def push(self, article, fn):
        raise NotImplementedError
