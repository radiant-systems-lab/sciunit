
import sciunit2.workspace

from contextlib import contextmanager
import os


# returns the pkgdir and original command used
# to execute execution 'rev'
@contextmanager
def CheckoutContext(rev):
    emgr, repo = sciunit2.workspace.current()
    with emgr.exclusive():
        orig = emgr.get(rev).cmd
        pkgdir = os.path.join(repo.location, 'cde-package')
        repo.cleanup(pkgdir)
        repo.checkout(rev)
        yield pkgdir, orig


@contextmanager
def CheckoutContext_Diff(rev):
    emgr, repo = sciunit2.workspace.current()
    with emgr.exclusive():
        orig = emgr.get(rev).cmd
        pkgdir = os.path.join(repo.location, 'cde-package' + rev)
        repo.cleanup(pkgdir)
        repo.checkout(rev)
        yield pkgdir, orig
