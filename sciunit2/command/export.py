from __future__ import absolute_import

import os
import re
import subprocess
import sys
from tqdm import tqdm
from subprocess import CalledProcessError

from sciunit2.command import AbstractCommand
from sciunit2.command.context import CheckoutContext
from sciunit2.exceptions import CommandLineError, MalformedExecutionId
from sciunit2.util import quoted_format
from sciunit2.workspace import _mkdir_p
from sciunit2.workspace import at

from getopt import getopt


def python_paths(log_file, cde_root_dir):
    """
    Extracts the following information from the provenance log file
    1. site-packages dir path(s)
    (more than one possible in case of virtual environments)
    2. python executable path
    3. python version
    """
    with open(log_file) as f:
        print(log_file)
        print(cde_root_dir)
        line = f.readline()
        found = False
        pkg_dir_lines = []
        while line:
            print(line)
            line = line.strip()
            # reading python executable path from the
            # first line after comments in the log file
            if not found and not line.startswith('#'):
                splits = line.split(' ')
                if len(splits) >= 5:
                    python_path = splits[4]
                    python_path = cde_root_dir + python_path
                    found = True
                    continue
            if line.endswith("site-packages"):
                pkg_dir_line = line.split(" ")[-1]
                py_version = pkg_dir_line.split('/')[-2]
                if pkg_dir_line not in pkg_dir_lines:
                    pkg_dir_lines.append(pkg_dir_line)
            line = f.readline()

    site_pkg_dirs = []
    for pkg_dir_line in pkg_dir_lines:
        site_pkg_dir = cde_root_dir + pkg_dir_line
        with os.scandir(site_pkg_dir) as sc:
            if any(sc):
                site_pkg_dirs.append(site_pkg_dir)

    return site_pkg_dirs, python_path, py_version


def find_pkg_list(site_package_dirs):
    """
    Retrieves a list of virtualenv packages
    from the site-packages directory
    """
    try:
        pkg_list = []
        for site_pkg_dir in site_package_dirs:
            packages = []
            info_packages = []
            versions = []
            # step 1:
            # find dirs having .dist-info or .egg-info names
            try:
                for dir_ in os.listdir(site_pkg_dir):
                    if ".dist-info" in dir_ or ".egg-info" in dir_:
                        dir_path = os.path.join(site_pkg_dir, dir_)
                        # an egg-info can also sometimes be a file
                        if os.path.isfile(dir_path):
                            info_packages.append(dir_)
                        else:
                            with os.scandir(dir_path) as sc:
                                if any(sc):
                                    info_packages.append(dir_)
            except Exception as ex:
                print('Error finding package list. aborting!')
                return None
                # if packages are found in step 1, find their versions

            for package in info_packages:
                pkg, ver = package.split("-")[:2]
                if "dist" in ver:
                    ver = ".".join(ver.split(".")[:-1])
                packages.append(pkg)
                versions.append(ver)

            # step 2:
            # if no dist-info or egg-info found in step 1,
            # then the python packages are in separate directories.
            package_paths = []
            # read package dirs
            for (dirpath, dirnames, filenames) in os.walk(site_pkg_dir):
                for dirname in dirnames:
                    if dirname == '__pycache__' or ".dist-info" in dirname \
                            or ".egg-info" in dirname:
                        continue
                    package_path = os.path.join(dirpath, dirname)
                    with os.scandir(package_path) as sc:
                        if any(sc):
                            package_paths.append(package_path)
                            packages.append(dirname)
                break   # just need dirs at the top-level in site_pkg_dir

            # find the package versions for the packages found in step 2
            # versions can generally be found from the __init__.py, version.py,
            # __version__.py, etc. files present in each package dir
            for package_path in package_paths:
                for (dirpath, dirnames, filenames) in os.walk(package_path):
                    version_file = None
                    version = None
                    version_file_list = list(filter(lambda file: 'version' in file, filenames))
                    if version_file_list:
                        version_file = version_file_list[0]
                    else:
                        #  check for version detail in __init__.py
                        if '__init__.py' in filenames:
                            version_file = '__init__.py'
                    if version_file:
                        # extract version number from the file
                        with open(os.path.join(dirpath, version_file)) as f:
                            lines = f.readlines()
                            for line in lines:
                                version_line_list = re.findall(r'^_*version_*\s*=', line)
                                if version_line_list:
                                    version_split = line.split('=')
                                    if version_split and len(version_split) >= 2:
                                        version = version_split[1].strip()
                                        version = version.strip('"').strip('\'')
                                        version = str(version)
                                        # confirm its a number
                                        if not version[:1].isdigit():
                                            version = None
                    versions.append(version)
                    break
            pkg_list = list(zip(packages, versions))

        return pkg_list
    except Exception as ex:
        print('Error finding package list. aborting!')
        return None


def write_req_file(py_version, pkg_list, filename="requirements.txt"):
    """
    Writes the requirements.txt file.
    Also returns them in a string format
    """
    with open(filename, "w") as f:
        f.write("# for version: {0}\n".format(py_version))
        pkg_str = ''
        for pkg, ver in pkg_list:
            version = ''
            if ver:
                version = '==' + ver
            f.write(pkg + version + '\n')
            pkg_str += pkg + version + '\n'
        # add sciunit as a dependency for later use
        f.write('sciunit2\n')
        pkg_str += 'sciunit2\n'
    return pkg_str


# this class exports the dependencies of an execution
# and stores them in a requirements.txt file
class ExportCommand(AbstractCommand):
    name = 'export'

    # export can be called as:
    # sciunit export e1 [virtualenv]
    # where e1 is the mandatory execution id
    # if argument virtualenv is given, create
    # requirements.txt file and use it to instantiate
    # a new virtual environment in virtualenv,
    # install all Python dependencies in it.
    @property
    def usage(self):
        return [('export <execution id> [virtualenv]',
                 'Exports the dependencies of <execution id> into requirements.txt.\n'
                 'Optionally creates new virtualenv instance and '
                 'installs all python dependencies in it.\n')]

    def run(self, args):
        optlist, args = getopt(args, '')
        if len(args) < 1:
            raise CommandLineError
        eid = args[0]
        # check if eid is of the form en
        # i.e., a valid execution id format
        if not re.match(r'^e[1-9]\d*$', eid):
            raise MalformedExecutionId
        create_venv = False
        if len(args) == 2:
            if args[1] == 'virtualenv':
                create_venv = True
            else:
                raise CommandLineError

        # checkout eid
        with CheckoutContext(eid) as (cde_pkg_dir, orig):
            # set the various dir paths
            project_dir = at()
            project_name = project_dir.split('/')[-1]
            home_dir = cde_pkg_dir + '/cde-root/home/'
            user_name = os.listdir(home_dir)[0]
            user_dir = os.path.join(home_dir, user_name)
            user_dir += '/*'
            data_dir = project_name + '-' + eid
            env_name = 'env_' + data_dir
            output_log = env_name + '.log'

            # find environment path from log file
            log_file = "provenance.cde-root.1.log"
            log_file_path = cde_pkg_dir + "/" + log_file
            cde_root_dir = cde_pkg_dir + "/cde-root"
            site_pkg_dirs, python_path, py_version = python_paths(log_file_path, cde_root_dir)
            if not site_pkg_dirs:
                print('Aborting export! Environment paths not found')
                return None
            # find Python packages
            pkg_list = find_pkg_list(site_pkg_dirs)
            # write requirements file
            if pkg_list is not None:
                req_file = eid + "-requirements.txt"
                pkg_str = write_req_file(py_version, pkg_list, req_file)
                if create_venv:
                    retcode = 0
                    # 1. install virtualenv using pip(assuming pip is installed)
                    try:
                        retcode ^= subprocess.call(sys.executable + ' -m pip install' +
                                                   ' --force-reinstall' +
                                                   ' virtualenv &>' + output_log,
                                                   shell=True, executable='/bin/bash')
                    except CalledProcessError as err:
                        print(err.stderr)
                        print('Aborting export! Error installing virtualenv')
                        print('Detailed output log can be found in: ' + output_log)
                        return None
                    if retcode != 0:
                        print('Aborting export! Error installing virtualenv')
                        print('Detailed output log can be found in: ' + output_log)
                        return None

                    # 2. create new environment using virtualenv and
                    # install all Python dependencies in it
                    print('Creating new virtual environment...')
                    retcode ^= subprocess.call('`which virtualenv` ' + env_name
                                               + ' &>>' + output_log, shell=True, executable='/bin/bash')
                    if retcode == 0:
                        print('Installing Python packages...')
                        env_python_path = env_name + '/bin/python'
                        for pkg in tqdm(pkg_str.splitlines()):
                            cmd = env_python_path + ' -m pip install ' + pkg + ' &>> ' + output_log
                            subprocess.call(cmd, shell=True, executable='/bin/bash')
                    else:
                        print('Aborting export! Error installing dependencies')
                        print('Detailed output log can be found in: ' + output_log)
                        return None
                    if retcode != 0:
                        print('Aborting export!')
                        print('Detailed output log can be found in: ' + output_log)
                        return None

                    # 3. create new folder in cwd and bring all code+data
                    # in /home/<user> there
                    _mkdir_p(data_dir)
                    subprocess.call('cp -r ' + user_dir + ' ' + data_dir, shell=True)
                    print("A new virtual environment '" + env_name + "' successfully " +
                          "created with your Python packages.\n"
                          "Detailed output log can be found in: " + output_log)
                    print('You can activate the virtual environment as follows:\n'
                          '\tsource ' + env_name + '/bin/activate')
                    print('Your code and data have been copied to the dir: '
                          + data_dir + '\n')
                    print('To deactivate the environment, enter: deactivate')
                    print('Make sure to run the following command from your shell once:')
                    print('\texport SSL_CERT_DIR=/etc/ssl/certs/')
            else:
                print('Export not successful!')
                print('Detailed output log can be found in: ' + output_log)
                return None

        return eid

    def note(self, eid):
        return quoted_format('Exported python dependencies of execution {0} \n', eid)
