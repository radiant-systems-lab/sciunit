from __future__ import absolute_import

from sciunit2.util import quoted
from sciunit2 import timestamp
import sciunit2.workspace

from humanfriendly.terminal.spinners import Spinner


# This class commits the most recent execution to
# the de-duplication engine and the database.
# A spinning animation is displayed as feedback
# to the end-user during the entire time.
class CommitMixin(object):
    def do_commit(self, pkgdir, rev, emgr, repo):
        with Spinner(label='Committing') as sp:
            # adds the execution to de-duplication engine
            sz = repo.checkin(rev, pkgdir, sp)
        # adds the execution to the database
        commit = emgr.commit(sz)
        last_id = emgr.get_last_id()
        return (last_id, repo,) + commit

    def note(self, aList):
        return "\n[%s e%s] %s\n Date: %s\n" % (
            sciunit2.workspace.project(aList[1].location),
            aList[0],
            quoted(aList[3].cmd),
            timestamp.fmt_rfc2822(aList[3].started))
