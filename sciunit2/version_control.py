from __future__ import absolute_import

from sciunit2.exceptions import CommandError
from sciunit2.util import quoted_format
import sciunit2.libexec

import subprocess
from subprocess import PIPE
import os
import shutil
import errno
from backports.tempfile import TemporaryDirectory


# this class maintains the de-duplication engine
# and supports the necessary operations to
# store and retrieve execution instances
class Vvpkg(object):
    __slots__ = 'location'

    def __init__(self, location):
        self.location = location

    # adds a new execution to the de-duplication engine
    def checkin(self, rev, pkgdir, spinner):
        parent, name = os.path.split(os.path.abspath(pkgdir))
        # Let filesystem settle before trying to tar it up
        # This avoids "file changed as we read it"
        os.sync()
        # creates a tar file from dir 'name' in 'parent' dir,
        # writes it to stdout, then commits it to
        # de-duplication engine using 'vv' under the 'rev' eid
        # after reading from stdin
        cmd = quoted_format('tar cf - -C {1} {2} | {0} commit {3} -',
                            sciunit2.libexec.vv.which,
                            parent, name, rev)
        p = subprocess.Popen(cmd, shell=True, cwd=self.location, stderr=PIPE)
        # spinner creates a spinning animation as feedback
        # for users to display indefinite activity
        while p.poll() is None:
            spinner.step()
            spinner.sleep()
        _, err = p.communicate()
        if p.returncode == 0:
            self.cleanup(pkgdir)
            last_line = err.strip().split(b"\n")[-1]
            return int(last_line)
        else:
            raise CommandError('execution %r already exists' % rev
                               if self.__found(rev) else err)

    # brings out the execution identified by 'rev'
    # from the de-duplication engine
    def checkout(self, rev):
        cmd = quoted_format('{0} checkout {1} - | tar xf -',
                            sciunit2.libexec.vv.which, rev)
        p = subprocess.Popen(cmd, shell=True, cwd=self.location, stderr=PIPE)
        _, err = p.communicate()
        if p.wait() != 0:
            raise CommandError('execution %r not found' % rev
                               if not self.__found(rev) else err)

    # brings out the execution identified by 'rev'
    # from the de-duplication engine
    def checkout_Parallel(self, rev):
        rev_repo = os.path.join(self.location, rev)
        self._mkdir_p(rev_repo)
        self.cleanup(os.path.join(rev_repo, 'cde-package'))
        cmd = quoted_format('{0} checkout {1} - | tar xf - -C {2}',
                            sciunit2.libexec.vv.which, rev, rev_repo)
        p = subprocess.Popen(cmd, shell=True, cwd=self.location, stderr=PIPE)
        _, err = p.communicate()
        print("hi in checkout parallel"+cmd)
        if p.wait() != 0:
            raise CommandError('execution %r not found' % rev
                               if not self.__found(rev) else err)

    def checkout_Diff(self, rev):
        cmd = quoted_format('{0} checkout {1} - | tar xf -',
                            sciunit2.libexec.vv.which, rev)
        temp_repo = os.path.join(self.location, 'cde-package')
        self.cleanup(temp_repo)
        p = subprocess.Popen(cmd, shell=True, cwd=self.location, stderr=PIPE)
        _, err = p.communicate()
        if p.wait() != 0:
            raise CommandError('execution %r not found' % rev
                               if not self.__found(rev) else err)
        diff_repo = os.path.join(self.location, 'Diff')
        rev_repo = os.path.join(diff_repo, rev)
        self._mkdir_p(rev_repo)
        self.cleanup(os.path.join(rev_repo, 'cde-package'))
        shutil.move(temp_repo, rev_repo)

    def unlink(self, rev):
        try:
            os.unlink(self.__physical(rev))
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise  # pragma: no cover

    def chain_rename(self, revls):
        with TemporaryDirectory(dir=self.location) as dname:
            for orig, _ in revls:
                os.link(self.__physical(orig), os.path.join(dname, orig))
            for from_, to in revls:
                os.rename(os.path.join(dname, from_), self.__physical(to))

    def cleanup(self, pkgdir):
        shutil.rmtree(pkgdir, ignore_errors=True)

    def __found(self, rev):
        return os.path.isfile(self.__physical(rev))

    def __physical(self, rev):
        return os.path.join(self.location, '%s.json' % rev)

    def _mkdir_p(self, path):
        try:
            os.makedirs(path)
            return True
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                return False
            else:
                raise
