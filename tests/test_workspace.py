
from nose.tools import *
import os

import sciunit2.workspace


def test_location():
    p = sciunit2.workspace.location_for('.hidden')
    assert_true(p.startswith(os.path.expanduser('~')))
    assert_true(p.endswith('.hidden'))
