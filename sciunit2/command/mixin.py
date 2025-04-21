from __future__ import absolute_import

from sciunit2.util import quoted
from sciunit2 import timestamp
import sciunit2.workspace
import threading

from humanfriendly.terminal.spinners import Spinner


# This class commits the most recent execution to
# the de-duplication engine and the database.
# A spinning animation is displayed as feedback
# to the end-user during the entire time.
class CommitMixin(object):

    lock = threading.Lock()

    def do_commit(self, pkgdir, rev, emgr, repo):
        with Spinner(label='Committing') as sp:
            # adds the execution to de-duplication engine
            sz = repo.checkin(rev, pkgdir, sp)
        # adds the execution to the database
        return (repo.location,) + emgr.commit(sz)

    def do_commit_parallel(self, pkgdir, emgr, repo, args):
        with self.lock :
            rev = emgr.add(args)
            with Spinner(label='Committing') as sp:
                # adds the execution to de-duplication engine
                sz = repo.checkin(rev, pkgdir, sp)
            # adds the execution to the database
            return (repo.location,) + emgr.commit(sz)

    def note(self, aList):
        return "\n[%s %s] %s\n Date: %s\n" % (
            sciunit2.workspace.project(aList[0]),
            aList[1],
            quoted(aList[2].cmd),
            timestamp.fmt_rfc2822(aList[2].started))
