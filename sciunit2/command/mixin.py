from sciunit2.util import quoted
from sciunit2 import timestamp
import sciunit2.security
import sciunit2.workspace

from humanfriendly.terminal.spinners import Spinner


# This class commits the most recent execution to
# the de-duplication engine and the database.
# A spinning animation is displayed as feedback
# to the end-user during the entire time.
class CommitMixin(object):
    def do_commit(self, pkgdir, rev, emgr, repo):
        protection = sciunit2.security.protect_execution(pkgdir, rev)
        with Spinner(label='Committing') as sp:
            # adds the execution to de-duplication engine
            sz = repo.checkin(rev, pkgdir, sp)
        # adds the execution to the database
        result = (repo.location,) + emgr.commit(sz)
        if protection.get('protected'):
            sciunit2.security.cache_shared_key(repo.location, rev,
                                               protection['share_key'])
            return result + (protection,)
        return result

    def note(self, aList):
        msg = "\n[%s %s] %s\n Date: %s\n" % (
            sciunit2.workspace.project(aList[0]),
            aList[1],
            quoted(aList[2].cmd),
            timestamp.fmt_rfc2822(aList[2].started))
        if len(aList) > 3 and aList[3].get('protected'):
            protection = aList[3]
            msg += (
                " Portable secret key: {key}\n"
                " Protected artifacts: {artifact_count}, redacted files: {file_count}\n"
                " Run 'sciunit unlock {rev} --key <shared-key>' on the repeat side.\n"
            ).format(key=protection['share_key'],
                     artifact_count=protection['artifact_count'],
                     file_count=protection['file_count'],
                     rev=aList[1])
        return msg
