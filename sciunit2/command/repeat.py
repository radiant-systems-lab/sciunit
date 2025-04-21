from __future__ import absolute_import

from sciunit2.command import AbstractCommand
from sciunit2.command.context import CheckoutContext_Parallel
from sciunit2.exceptions import CommandLineError
import sciunit2.core

from getopt import getopt
import sys


class RepeatCommand(AbstractCommand):
    name = 'repeat'

    @property
    def usage(self):
        return [('repeat <execution id> [<args...>]',
                 "Repeat the execution of <execution id>")]

    def run(self, args):
        optlist, args = getopt(args, '')
        if not args:
            raise CommandLineError
        with CheckoutContext_Parallel(args[0]) as (pkgdir, orig):
            sys.exit(sciunit2.core.repeat(pkgdir, orig, args[1:]))
