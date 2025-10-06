
from unittest import mock
import unittest
import os
import shutil
from pathlib import Path

import sciunit2.cli
import sciunit2.workspace


class LocalCase(unittest.TestCase):
    def setUp(self):
        self.workspace_patch = mock.patch(
            'sciunit2.workspace.location_for',
            lambda s: os.path.join('tmp', s))
        self.workspace_patch.start()

    def tearDown(self):
        self.workspace_patch.stop()
        shutil.rmtree('tmp', True)


def sciunit(*args):
    with mock.patch('sys.argv', ['x'] + list(args)):
        sciunit2.cli.main()


def touch(_path):
    dirs = _path.rsplit("/", 1)[0]
    if len(dirs) > 0:
        mkdir(dirs)
    Path(_path).touch()


def mkdir(_path):
    Path(_path).mkdir(parents=True, exist_ok=True)
