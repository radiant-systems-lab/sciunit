from __future__ import absolute_import

import sciunit2.workspace
import sciunit2.filelock

from contextlib import contextmanager
import os

import shutil
import time

from getopt import getopt

# returns the pkgdir and original command used
# to execute execution 'rev'
@contextmanager
def CheckoutContext(rev):
    emgr, repo = sciunit2.workspace.current()
    lock = sciunit2.filelock.FileLock(os.path.join(repo.location ,'lockfile'))
    lock.acquire()
    try:
        with emgr.exclusive():
            orig = emgr.get(rev).cmd
            pkgdir = os.path.join(repo.location, 'cde-package')
            pkgdir_rev = os.path.join(repo.location, rev, 'cde-package')
            repo.cleanup(pkgdir)
            repo.cleanup(pkgdir_rev)
            repo.checkout(rev)
            shutil.copytree(pkgdir, pkgdir_rev)
            yield pkgdir_rev, orig
    finally:
        lock.release()

@contextmanager
def CheckoutContext_Diff(rev):
    emgr, repo = sciunit2.workspace.current()
    with emgr.exclusive():
        orig = emgr.get(rev).cmd
        pkgdir = os.path.join(repo.location, 'cde-package' + rev)
        repo.cleanup(pkgdir)
        repo.checkout(rev)
        yield pkgdir, orig
