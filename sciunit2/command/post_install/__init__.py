
from sciunit2.command import AbstractCommand

from getopt import getopt
import os
import pwd
import tempfile
import pkg_resources
from shutil import copyfileobj
from contextlib import closing
from humanfriendly import format_path


class PostInstallCommand(AbstractCommand):
    name = 'post-install'

    @property
    def usage(self):
        return []

    def run(self, args):
        optlist, args = getopt(args, '')
        self.install_shell_piece({
            'tcsh': ('sciunit-completion.tcsh', '~/.complete', '~/.cshrc'),
            'bash': ('sciunit-completion.bash', '~/.bash_completion',
                     '~/.bashrc'),
        })

    def install_shell_piece(self, d):
        sh_str = pwd.getpwuid(os.getuid()).pw_shell
        sh_name = ''
        for s in d.keys():
            if sh_str.endswith('/' + s):
                sh_name = s
                break
        if sh_name:
            self.patch_shell_script(*d[sh_name])

    @staticmethod
    def patch_shell_script(from_, to, rcfile):
        a = '# --------- BEGIN -- maintained by sciunit --------------\n'
        b = '# --------- END ---- maintained by sciunit --------------\n'
        to_ = os.path.expanduser(to)
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(to_),
                                         prefix='pip-tmp') as tmp:
            script = pkg_resources.resource_stream(__name__, from_)
            try:
                with closing(script) as g, closing(open(to_, 'a+')) as f:
                    f.seek(0)
                    for ln in f:
                        if ln == a:
                            break
                        tmp.write(ln.encode())
                    tmp.write(a.encode())
                    copyfileobj(g, tmp)
                    tmp.write(b.encode())
                    for ln in f:
                        if ln == b:
                            break
                    for ln in f:
                        tmp.write(ln.encode())
                    os.rename(tmp.name, to_)
                    tmp.delete = False
                    tmp._closer.delete = False
                print("x %s" % to)

            except EnvironmentError:
                print('Unable to patch %s.  Please copy\n\n    %s\n\n'
                      'to a subdirectory of your home directory '
                      'and "source" it in %s.' %
                      (to, format_path(script.name), rcfile))
