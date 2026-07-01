from sciunit2.command import AbstractCommand
from sciunit2.exceptions import CommandLineError
import sciunit2.security
import sciunit2.workspace

from getopt import getopt


class UnlockCommand(AbstractCommand):
    name = 'unlock'

    @property
    def usage(self):
        return [('unlock <execution id> --key <shared-key>',
                 'Cache a shared key locally so repeat can restore protected files')]

    def run(self, args):
        optlist, args = getopt(args, '', ['key='])
        if len(args) != 1:
            raise CommandLineError
        key = None
        for op, value in optlist:
            if op == '--key':
                key = value
        if not key:
            raise CommandLineError

        emgr, repo = sciunit2.workspace.current()
        with emgr.shared():
            emgr.get(args[0])
        sciunit2.security.cache_shared_key(repo.location, args[0], key)
        return args[0]

    def note(self, user_data):
        return 'Cached shared key for %s\n' % (user_data,)
