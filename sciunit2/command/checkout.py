from __future__ import absolute_import

from sciunit2.command import AbstractCommand
from sciunit2.command.context import CheckoutContext_Parallel
from sciunit2.exceptions import CommandLineError
from sciunit2.util import quoted_format
import sciunit2.core

from getopt import getopt
import sys


class CheckoutCommand(AbstractCommand):
    name = 'checkout'

    @property
    def usage(self):
        return [('checkout <execution id>',
                 "Checkout the execution of <execution id>")]

    def run(self, args):
        optlist, args = getopt(args, '')
        if len(args) != 1:
            raise CommandLineError
        with CheckoutContext_Parallel(args[0]) as (pkgdir, _):
            return pkgdir

    def note(self, project_dir):
        return quoted_format('Checked out at: {0}\n', project_dir)
