from __future__ import absolute_import

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

    def __call__(self, args,cwd=None, **kwargs):
        return subprocess.Popen([self.which] + args,cwd=cwd, **kwargs)


ptu = Process('ptu')
vv = Process('vv')
scripter = Process('scripter')
