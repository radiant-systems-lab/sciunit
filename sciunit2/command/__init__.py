
import abc
from abc import abstractmethod


class AbstractCommand:
    __metaclass__ = abc.ABCMeta

    name = NotImplemented

    # this method is used to print the usage
    # format of the command
    @property
    @abstractmethod
    def usage(self):
        raise NotImplementedError

    @abstractmethod
    def run(self, args):
        raise NotImplementedError

    # this method is used to print out the
    # output after the command execution
    def note(self, user_data):
        raise NotImplementedError
