from __future__ import absolute_import

from sciunit2.command import AbstractCommand
from sciunit2.exceptions import CommandLineError
from sciunit2.util import quoted_format
import sciunit2.workspace

from getopt import getopt


# this class removes the sciunit project
# under ~/sciunit identified by <name>
class RemoveCommand(AbstractCommand):
    name = 'remove'

    @property
    def usage(self):
        return [('remove <name>',
                 'Remove the sciunit ~/sciunit/<name>')]

    def run(self, args):
        optlist, args = getopt(args, '')
        if len(args) != 1:
            raise CommandLineError
        else:
            print('This will remove all files in ' + args[0] +
                  ' permanently.\nAre you sure',
                  'you want to proceed? \nEnter (y/n)')
            confirm = input()
            confirm = confirm.lower()
            if confirm == 'y':
                sciunit2.workspace.delete(args[0])
                return sciunit2.workspace.close(args[0])
            else:
                return None

    def note(self, project_dir):
        return quoted_format(
            'Successfully removed sciunit project {0}\n',
            project_dir)
