
import os
import subprocess


# returns path for the process file 'cmd'
def pathfor(cmd):
    return os.path.join(os.path.dirname(__file__), cmd)


class Process(object):
    __slots__ = 'name'

    def __init__(self, name):
        self.name = name

    @property
    def which(self):
        return pathfor(self.name)

    def __call__(self, args, **kwargs):
        return subprocess.Popen([self.which] + args, **kwargs)


ptu = Process('ptu')
vv = Process('vv')
scripter = Process('scripter')
