
from sciunit2.command import AbstractCommand
from sciunit2.command.mixin import CommitMixin
from sciunit2.exceptions import CommandLineError
from sciunit2.util import path_injection_for
import sciunit2.core
import sciunit2.workspace

from getopt import getopt
from pkg_resources import resource_filename


class ExecCommand(CommitMixin, AbstractCommand):
    name = 'exec'

    @property
    def usage(self):
        return [('exec <executable> [<args...>]',
                 'Capture an execution of the given command line'),
                ('exec -i',
                 "Capture user's interactions inside a shell")]

    def run(self, args):
        optlist, args = getopt(args, 'i')
        if bool(optlist) == bool(args):
            raise CommandLineError
        emgr, repo = sciunit2.workspace.current()
        with emgr.exclusive():
            rev = emgr.add(args)
            if optlist:
                standin_fn = resource_filename(__name__, 'sciunit')
                sciunit2.core.shell(env=path_injection_for(standin_fn))
            else:
                sciunit2.core.capture(args)
            return self.do_commit('cde-package', rev, emgr, repo)
