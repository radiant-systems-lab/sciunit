from __future__ import absolute_import

from sciunit2.command import AbstractCommand
from sciunit2.command.mixin import CommitMixin
from sciunit2.exceptions import CommandLineError
from sciunit2.util import path_injection_for
import sciunit2.core
import sciunit2.workspace
import os
import threading

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
            if optlist:
                rev = emgr.add(args)
                standin_fn = resource_filename(__name__, 'sciunit')
                sciunit2.core.shell(env=path_injection_for(standin_fn))
                results = self.do_commit('cde-package', rev, emgr, repo)
            else:
                # make a new directory for the execution
                thread_id = threading.current_thread().ident
                directory_name = f"thread_{thread_id}"
                os.makedirs(directory_name, exist_ok=True)

                sciunit2.core.capture(args,cwd =directory_name)
                results = self.do_commit_parallel(os.path.join(directory_name,'cde-package'), emgr, repo,args)

                os.rmdir(directory_name)

            return results
