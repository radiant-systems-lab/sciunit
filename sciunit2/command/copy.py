from __future__ import absolute_import

from sciunit2.command import AbstractCommand
from sciunit2.exceptions import CommandLineError
import sciunit2.workspace
import sciunit2.archiver
import sciunit2.s3
from sciunit2.util import quoted_format

from getopt import getopt


class CopyCommand(AbstractCommand):
    name = 'copy'

    @property
    def usage(self):
        return [('copy', 'Copy the sciunit and obtain a token for opening '
                         'it over the Internet'),
                ('copy -n', 'Archive the sciunit to ~/sciunit/<name>.zip')]

    def run(self, args):
        optlist, args = getopt(args, 'n')
        if args:
            raise CommandLineError
        emgr, repo = sciunit2.workspace.current()
        with emgr.shared():
            fn = sciunit2.archiver.make(repo.location)
            if optlist:
                print(fn)
            else:
                print(sciunit2.s3.live(fn))

    def note(self, user_data):
        return quoted_format('Copied sciunit at {0}\n', user_data)
