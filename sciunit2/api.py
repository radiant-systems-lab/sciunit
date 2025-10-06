
import sys
import sciunit2.cli


def main(*args):
    sys.argv = ['x'] + list(args)
    sciunit2.cli.main()


class Sciunit:
    def exec(*args):
        # interactive exec is not supported with the API
        args = ('exec',) + args[1:]
        main(*args)

    def commit(*args):
        args = ('commit',) + args[1:]
        main(*args)

    def copy(*args):
        args = ('copy',) + args[1:]
        main(*args)

    def create(*args):
        args = ('create',) + args[1:]
        main(*args)

    def diff(*args):
        args = ('diff',) + args[1:]
        main(*args)

    def given(*args):
        args = ('given',) + args[1:]
        main(*args)

    def list(*args):
        args = ('list',) + args[1:]
        main(*args)

    def open(*args):
        args = ('open',) + args[1:]
        main(*args)

    def push(*args):
        args = ('push',) + args[1:]
        main(*args)

    def repeat(*args):
        args = ('repeat',) + args[1:]
        main(*args)

    def rm(*args):
        args = ('rm',) + args[1:]
        main(*args)

    def show(*args):
        args = ('show',) + args[1:]
        main(*args)

    def sort(*args):
        args = ('sort',) + args[1:]
        main(*args)
