# Note: Converted
from __future__ import absolute_import

import os
import shlex
import tempfile
import itertools
import errno
from glob import glob


def quoted_format(fmt, *args):
    return fmt.format(*map(shlex.quote, args))


def quoted(args):
    return ' '.join(map(shlex.quote, args))


# expands 'ptrn' into a list of filenames in the style of unix glob(3),
# substitutes the first occurrence of %, if any, in 'args'
# of the repeat mini-command with those filenames
def globsub(ptrn, args):
    files = glob(ptrn)
    try:
        i = args.index('%')
        args[i:i + 1] = files
    except ValueError:
        pass
    return files, args


def _temp_names_derivedfrom(base, sep):
    yield base
    names = tempfile._get_candidate_names()
    for name in itertools.islice(names, 0, tempfile.TMP_MAX):
        yield base + sep + name


def mkdir_derivedfrom(base, sep, mode=0o777):
    base = os.path.normpath(base)

    for p in _temp_names_derivedfrom(base, sep):
        try:
            os.mkdir(p, mode)
            return p
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                continue
            raise  # pragma: no cover

    raise IOError(errno.EEXIST, "No usable temporary directory name found")


def path_injection_for(fn):
    env = os.environ.copy()
    env['PATH'] = ':'.join([os.path.dirname(fn), env['PATH']])
    return env


def make_executable(fn):
    mode = os.stat(fn).st_mode
    mode |= (mode & 0o444) >> 2
    os.chmod(fn, mode)


class Chdir(object):
    __slots__ = ['cwd', 'target']

    def __init__(self, target):
        self.cwd = os.getcwd()
        self.target = target

    def __enter__(self):
        os.chdir(self.target)
        return self

    def __exit__(self, *args):
        os.chdir(self.cwd)
