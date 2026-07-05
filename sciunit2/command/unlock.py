from sciunit2.command import AbstractCommand
from sciunit2.exceptions import CommandLineError
import sciunit2.security
import sciunit2.workspace

class UnlockCommand(AbstractCommand):
    name = 'unlock'

    @property
    def usage(self):
        return [('unlock <execution id> --key <shared-key>',
                 'Cache a shared key locally so repeat can restore protected files')]

    def run(self, args):
        if len(args) != 3 or args[1] != '--key':
            raise CommandLineError
        rev = args[0]
        key = args[2]
        if not key:
            raise CommandLineError

        emgr, repo = sciunit2.workspace.current()
        with emgr.shared():
            emgr.get(rev)
        sciunit2.security.cache_shared_key(repo.location, rev, key)
        return rev

    def note(self, user_data):
        return 'Cached shared key for %s\n' % (user_data,)
