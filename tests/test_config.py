
from nose.tools import *

import sciunit2.config


def test_indent():
    x = sciunit2.config.Config()
    x.section('a', 'doe')['k'] = 1
    x.section('a')['k'] = 2
    x.section('a')['g'] = 3
    ls = x.write()

    assert_equal(ls, ['[a "doe"]',
                      '	k = 1',
                      '[a]',
                      '	k = 2',
                      '	g = 3'])

    with assert_raises(sciunit2.config.ConfigObjError):
        x.section('a', '"master"')
