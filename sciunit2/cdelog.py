import builtins

from sciunit2.util import quoted_format, quoted

import shlex
import json
import os
import errno


# opens cde.log file as Script object
def open(fn, mode='r'):
    return Script(builtins.open(fn, mode))


# This class runs an arbitrary execution
# before it is committed to the database.
# It is named thus as if it is in detached state
# from the normal execution tree of sciunit executions.
class DetachedExecution(object):
    __slots__ = '__fn'

    # note: cde stands for code, data and environment
    # which is an application versioning tool that
    # ptu is built on top of.
    def __init__(self, _dir):
        # dir is location for cde-package/
        # __fn is location of cde.log
        self.__fn = os.path.join(_dir, 'cde.log')

    def getcmd(self):
        try:
            with open(self.__fn) as f:  # opens cde.log as a Script object
                ls = f.read_cmd()   # reads the commands from cde.log
            yield ls
        except IOError as exc:
            if exc.errno != errno.ENOENT:
                raise  # pragma: no cover

    # returns project dir path starting from ../cde-root/root/home/
    def cwd_on_host(self):
        with open(self.__fn) as f:
            return os.path.join(os.path.dirname(self.__fn), next(f)[1])

    def root_on_host(self):
        return os.path.join(os.path.dirname(self.__fn), 'cde-root')


# reads, writes and executes the execution
# script from cde-package/cde.log
class Script(object):
    __slots__ = ['__f', '__sh']

    def __init__(self, fp):
        self.__f = fp
        self.__sh = shlex.shlex(self.__f, posix=True)
        self.__sh.whitespace_split = True

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.__f.close()

    def prepend_cmd(self, args):
        content = self.__f.read()
        self.__f.seek(0)
        self.write_cmd(args)
        self.__f.write(content)

    def write_cmd(self, args):
        self.__f.write('# ')
        json.dump(args, self.__f)
        self.__f.write('\n')

    def read_cmd(self):
        ln = self.__f.readline()
        if ln.startswith('# ['):
            return json.loads(ln[2:])
        else:
            self.__sh.push_source(ln)
            return []

    def __iter__(self):
        return self

    def __next__(self):
        lno = 0
        ls = []
        while True:
            tok = self.__sh.get_token()
            if tok == self.__sh.eof:
                if ls:
                    break
                else:
                    raise StopIteration
            else:
                ls.append(tok)
                if not lno:
                    lno = self.__sh.lineno
                elif lno < self.__sh.lineno:
                    break
        return ls

    def printf(self, fmt, *args):
        self.__f.write(quoted_format(fmt, *args))

    def insert(self, args):
        print(quoted(args), file=self.__f)
