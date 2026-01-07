
from sciunit2.command import AbstractCommand
from sciunit2.exceptions import CommandLineError
from sciunit2.util import quoted_format
import sciunit2.workspace

from getopt import getopt


# this class creates a new sciunit project
# under ~/sciunit identified by <name>
class CreateCommand(AbstractCommand):
    name = 'create'

    @property
    def usage(self):
        return [('create [-f] <name>',
                 'Create and open a new sciunit under ~/sciunit/<name>.\n'
                 'The -f flag overwrites the existing directory if present.')]

    def run(self, args):
        optlist, args = getopt(args, 'f')
        if len(args) != 1:
            raise CommandLineError
        else:
            project_name = args[0].strip()
            if optlist:
                if optlist[0][0] == '-f':    # if force flag is provided
                    print('Warning: This will overwrite the existing sciunit!')
                    sciunit2.workspace.create(project_name, overwrite=True)
                else:
                    raise CommandLineError
            else:
                sciunit2.workspace.create(project_name)
            return sciunit2.workspace.open(project_name)

    def note(self, project_dir):
        return quoted_format('Opened empty sciunit at {0}\n', project_dir)
