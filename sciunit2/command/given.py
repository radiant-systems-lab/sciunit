from __future__ import absolute_import

import shutil
import os
import sys
from distutils.errors import DistutilsFileError
from getopt import getopt

import sciunit2.core
import sciunit2.workspace
from sciunit2.cdelog import DetachedExecution
from sciunit2.command import AbstractCommand
from sciunit2.command.context import CheckoutContext
from sciunit2.command.mixin import CommitMixin
from sciunit2.exceptions import CommandLineError, CommandError
from sciunit2.util import globsub


class GivenCommand(CommitMixin, AbstractCommand):
    name = 'given'

    @property
    def usage(self):
        return [('given <glob> repeat <execution id> [<%|args...>]',
                 "Repeat <execution id> with additional files or directories "
                 "specified by <glob>")]

    # args = <glob> repeat <execution id> <args for repeat>|%
    def run(self, args):
        optlist, args = getopt(args, '')
        if len(args) < 3 or args[1] != 'repeat':
            raise CommandLineError
        # args = <execution id> <file names in glob>
        files, args = globsub(args[0], args[2:])
        # files = list of files or dirs in <glob>
        # args = <execution id> list of args after % + files
        if not files:
            raise CommandError('no match')
        self.name = 'repeat'
        optlist, args = getopt(args, '')

        with CheckoutContext(args[0]) as (pkgdir, orig):
            try:
                de = DetachedExecution(pkgdir)
                if os.path.isabs(files[0]):
                    dst = de.root_on_host()  # project_dir/cde-package/cde-root
                    for f in files:
                        copytree(os.path.relpath(f, '/'), dst)
                    join_fn = str.__add__
                else:
                    # project dir inside ./cde-root/root/home
                    dst = de.cwd_on_host()
                    for f in files:
                        copytree(f, dst)
                    join_fn = os.path.join

                for fn in files:
                    target = join_fn(dst, fn)
                    if os.path.isdir(fn):
                        shutil.copytree(fn, target, dirs_exist_ok=True)
                    else:
                        shutil.copyfile(fn, target)

            except shutil.Error as e:
                raise CommandError(e)
            else:
                repeat_out = sciunit2.core.repeat(pkgdir, orig, args[1:])
                if repeat_out != 0:
                    sys.exit(repeat_out)
        emgr, repo = sciunit2.workspace.current()
        pkgdir = os.path.join(repo.location, 'cde-package')
        with emgr.exclusive():
            rev = emgr.add(args[1:])
            self.do_commit(pkgdir, rev, emgr, repo)
            return sys.exit(repeat_out)


def copytree(src, dst):
    if not os.path.isdir(src):
        path = src.rsplit("/", 1)[0]
    else:
        path = src
    os.makedirs(dst + "/" + path, exist_ok=True)
