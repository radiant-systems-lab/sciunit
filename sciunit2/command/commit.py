# Note: Converted

from sciunit2.command import AbstractCommand
from sciunit2.command.mixin import CommitMixin
from sciunit2.exceptions import CommandLineError, CommandError
from sciunit2.cdelog import DetachedExecution
import sciunit2.workspace

from getopt import getopt
import os


class CommitCommand(CommitMixin, AbstractCommand):
    name = 'commit'

    @property
    def usage(self):
        return [('commit', 'Commit the finishing state of the last repeat '
                           'command as a new execution')]

    def run(self, args):
        optlist, args = getopt(args, '')
        if args:
            raise CommandLineError
        emgr, repo = sciunit2.workspace.current()  # repo is vvpkg
        pkgdir = os.path.join(repo.location, 'cde-package')
        with emgr.exclusive():
            for cmd in DetachedExecution(pkgdir).getcmd():
                rev = emgr.add(cmd)
                return self.do_commit(pkgdir, rev, emgr, repo)
            else:
                raise CommandError('nothing to commit')
