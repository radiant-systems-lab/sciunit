from sciunit2.command import AbstractCommand
from sciunit2.command.context import CheckoutContext
from sciunit2.exceptions import CommandLineError, CommandError
import sciunit2.core
import sciunit2.security
import sciunit2.workspace

from getopt import getopt
import sys


class RepeatCommand(AbstractCommand):
    name = 'repeat'

    @property
    def usage(self):
        return [('repeat <execution id> [<args...>]',
                 "Repeat the execution of <execution id>")]

    def run(self, args):
        optlist, args = getopt(args, '')
        if not args:
            raise CommandLineError
        project_root = sciunit2.workspace.at()
        rev = args[0]
        if rev == 'latest':
            emgr, _ = sciunit2.workspace.current()
            with emgr.exclusive():
                rev, _ = emgr.last()
        with CheckoutContext(rev) as (pkgdir, orig):
            if sciunit2.security.package_requires_unlock(pkgdir):
                shared_key = sciunit2.security.cached_shared_key(project_root,
                                                                 rev)
                if not shared_key:
                    raise CommandError(
                        "execution %r is encrypted and cannot be repeated yet.\n"
                        "Run this command in a terminal, then come back and restart the Sciunit Repeat Kernel:\n"
                        "  sciunit unlock %s --key <shared-key>"
                        % (rev, rev))
                try:
                    sciunit2.security.validate_shared_key(pkgdir, shared_key)
                except CommandError:
                    raise CommandError(
                        "execution %r has an invalid cached unlock key.\n"
                        "Run this command with the correct shared key, then restart the Sciunit Repeat Kernel:\n"
                        "  sciunit unlock %s --key <shared-key>"
                        % (rev, rev))
                sciunit2.security.restore_execution(pkgdir, shared_key)
            sys.exit(sciunit2.core.repeat(pkgdir, orig, args[1:]))
