
from sciunit2.command import AbstractCommand
from sciunit2.command.list import run_listing
from sciunit2.exceptions import CommandLineError
import sciunit2.workspace

from getopt import getopt


class SortCommand(AbstractCommand):
    name = 'sort'

    @property
    def usage(self):
        return [('sort <execution ids...>',
                 'Reorder the executions to make the <execution ids...> '
                 'a consecutive subrange')]

    def run(self, args):
        optlist, args = getopt(args, '')
        if not args:
            raise CommandLineError
        emgr, repo = sciunit2.workspace.current()
        with emgr.exclusive():
            for ls in emgr.sort(args):
                repo.chain_rename(ls)
            run_listing(emgr)
