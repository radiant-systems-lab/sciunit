from __future__ import absolute_import

from sciunit2.exceptions import CommandLineError, CommandError
from sciunit2.command.create import CreateCommand
from sciunit2.command.open import OpenCommand
from sciunit2.command.exec_ import ExecCommand
from sciunit2.command.repeat import RepeatCommand
from sciunit2.command.list import ListCommand
from sciunit2.command.show import ShowCommand
from sciunit2.command.given import GivenCommand
from sciunit2.command.commit import CommitCommand
from sciunit2.command.rm import RmCommand
from sciunit2.command.sort import SortCommand
from sciunit2.command.push import PushCommand
from sciunit2.command.copy import CopyCommand
from sciunit2.command.checkout import CheckoutCommand
from sciunit2.command.post_install import PostInstallCommand
from sciunit2.command.diff import DiffCommand
from sciunit2.command.export import ExportCommand
from sciunit2.command.remove import RemoveCommand

import sys
from getopt import getopt, GetoptError
from io import StringIO
import textwrap
import pkg_resources
import os
import platform

__cmds__ = [CreateCommand, OpenCommand, ExecCommand, RepeatCommand,
            ListCommand, ShowCommand, GivenCommand, CommitCommand, RmCommand,
            SortCommand, PushCommand, CopyCommand, PostInstallCommand,
            DiffCommand, RemoveCommand, ExportCommand, CheckoutCommand]


def short_usage(out):
    out.write("usage: sciunit [--version] [--help]\n"
              "       sciunit <command> [<args...>]\n")


def subcommand_usage(out, cmds):
    buf = StringIO()
    for cmd in cmds:
        for ln in cmd.usage:
            msgs = textwrap.wrap(ln[1], 49)
            if len(ln[0]) > 18:
                buf.write("  sciunit %s\n" % ln[0])
            else:
                buf.write("  sciunit %-18s  %s\n" % (ln[0], msgs[0]))
                msgs.pop(0)
            for t in msgs:
                buf.write("                              %s\n" % t)
    out.write(buf.getvalue())


def err1(msg):
    sys.stderr.write("sciunit: %s\n" % (msg,))


def err2(msg1, msg2):
    sys.stderr.write("sciunit: %s: %s\n" % (msg1, msg2))


def main():
    try:
        _main(sys.argv[1:])
    except CommandLineError:
        short_usage(sys.stderr)
        sys.exit(2)
    except GetoptError as exc:
        err1(exc.msg)
        short_usage(sys.stderr)
        sys.exit(2)
    except EnvironmentError as exc:
        if hasattr(exc, 'filename') and exc.filename is not None:
            err2(exc.filename, exc.strerror)
        else:  # pragma: no cover
            err1(exc.strerror)
        sys.exit(1)


def _main(args):
    if platform.system().startswith('Linux') == False:
        err1('Platform is not supported')
        sys.exit(1)

    optlist, args = getopt(args, '', ['help', 'version', 'root='])
    if optlist:
        op, v = optlist[0]
        if op == '--help':
            short_usage(sys.stdout)
            print()
            subcommand_usage(sys.stdout, [cls() for cls in __cmds__])
            return
        elif op == '--version':
            print(pkg_resources.require("sciunit2")[0])
            return
        elif op == '--root':  # pragma: no cover
            import sciunit2.workspace
            sciunit2.workspace.location_for = lambda p: os.path.join(v, p)

    if args:
        for cls in __cmds__:
            if args[0] == cls.name:
                cmd = cls()
                try:
                    r = cmd.run(args[1:])
                    if r is not None:
                        sys.stderr.write(cmd.note(r))
                except CommandLineError:
                    subcommand_usage(sys.stderr, [cmd])
                    sys.exit(2)
                except GetoptError as exc:
                    err2(cmd.name, exc.msg)
                    subcommand_usage(sys.stderr, [cmd])
                    sys.exit(2)
                except CommandError as exc:
                    err2(cmd.name, exc)
                    sys.exit(1)
                except EOFError:
                    err1("End of file error!")
                break
        else:
            raise GetoptError('subcommand %r unrecognized' % args[0])
    else:
        raise CommandLineError
