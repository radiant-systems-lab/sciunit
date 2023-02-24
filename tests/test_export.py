from __future__ import absolute_import

import shutil

from nose.tools import *

from tests import testit
import os


class TestExport(testit.LocalCase):
    def test_all(self):
        py_file = 'export_example.py'
        self.create_sample_code(py_file)
        testit.sciunit('create', 'ok')
        testit.sciunit('exec', 'python', py_file)
        eid = 'e1'
        testit.sciunit('export', eid)
        req_file = eid + '-requirements.txt'
        assert_true(os.path.isfile(req_file))
        os.remove(req_file)
        os.remove(py_file)

        testit.sciunit('export', eid, 'virtualenv')
        data_dir = 'ok-' + eid
        env_dir = 'env_' + data_dir
        env_log = env_dir + '.log'
        assert_true(os.path.isfile(req_file))
        assert_true(os.path.isdir(env_dir))
        assert_true(os.path.isdir(data_dir))
        assert_true(os.path.isfile(env_log))
        os.remove(req_file)
        os.remove(env_log)
        shutil.rmtree(data_dir)
        shutil.rmtree(env_dir)

    def create_sample_code(self, py_file):
        py_code = "import numpy as np\n" \
                  "import requests\n" \
                  "import os\n" \
                  "print('cwd is: ' + os.getcwd())\n" \
                  "r = requests.get('https://python.org')\n" \
                  "print('status_code: ', r.status_code)\n" \
                  "np_arr = np.array([1, 2, 3, 4, 5])\n" \
                  "print('numpy array: ', np_arr)\n" \

        with open(py_file, 'w+') as f:
            f.write(py_code)
