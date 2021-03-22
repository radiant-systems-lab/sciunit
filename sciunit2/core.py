from __future__ import absolute_import

from sciunit2.exceptions import CommandError
from sciunit2.util import Chdir
from sciunit2.cdelog import open
import sciunit2.libexec

import os
import shutil
import subprocess


# capture the execution of commands from cde.log
def capture(args):
    sciunit2.libexec.ptu(args).wait()
    assert os.path.isdir('cde-package')
    with open('cde-package/cde.log', 'r+') as f:
        f.prepend_cmd(args)


# capture the execution of commands from interactive shell
def shell(env=None):
    print('Interactive capturing started; press Ctrl-D to end')
    sciunit2.libexec.ptu([sciunit2.libexec.scripter.which,
                          '-qi', 'cde.stdin'], env=env).wait()
    assert os.path.isdir('cde-package')
    print('Interactive capturing ended')
    shutil.move('cde.stdin', 'cde-package')
    with open('cde-package/cde.log') as f:
        cd, ls = f
    with open('cde-package/cde.log', 'w') as f:
        f.insert(cd)
        f.printf('{0} -qi /dev/null < {1}\n',
                 ls[0], os.path.relpath('cde.stdin', cd[1]))


def repeat(pkgdir, orig, newargs):
    if newargs:
        if not orig:
            raise CommandError(
                "interactive sciunit doesn't react to arguments")
        with Chdir(pkgdir):
            with open('cde.log') as f:
                cd, ls = f
            os.rename('cde.log', 'cde.log.1')
            with open('cde.log', 'w') as f:
                # adds the command in a comment
                f.write_cmd(orig[:1] + newargs)
                # dir to cd into for executing the commands
                f.insert(cd)
                # commands to execute with new arguments
                f.insert(ls[:1] + newargs)
    try:
        output = subprocess.check_output(['/bin/sh', 'cde.log'], cwd=pkgdir)
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        return exc.returncode
    else:
        print(output.decode('utf-8'))
        return 0
