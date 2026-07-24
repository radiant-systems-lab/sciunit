#!/usr/bin/env python
import version
import os
import subprocess
import gzip
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py


def localopen(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


class BuildCommand(build_py):
    def run(self):
        subprocess.check_call(['cmake', '-DCMAKE_BUILD_TYPE=Release'])
        subprocess.check_call(['make', '-j4'])
        subprocess.call(['apt-get', 'update'])
        build_py.run(self)
        _build_manpage('docs/sciunit.1.rst', 'sciunit.1.gz')


def _build_manpage(src, target):
    from docutils.core import publish_file
    from docutils.writers import manpage

    with gzip.open(target, 'wt') as f:
        publish_file(source_path=src,
                     destination=f,
                     writer=manpage.Writer())


setup(
    name='sciunit2',
    version=version.get_version(),
    description='Sciunit command line',
    author='Zhihao Yuan, Tanu Malik',
    author_email='pr@sciunit.run',
    maintainer='Zhihao Yuan',
    maintainer_email='lichray@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    keywords=['sciunit', 'reproducibility', 'container', 'versioning'],
    url='https://sciunit.run/',
    project_urls={
        'Homepage': 'https://sciunit.run/',
        'Documentation': 'https://sciunit.run/docs/',
        'Source': 'https://github.com/depaul-dice/sciunit',
    },
    long_description=localopen('README.rst').read(),
    setup_requires=['docutils'],
    install_requires=localopen('requirements.txt').readlines(),
    tests_require=localopen('test-requirements.txt').readlines(),
    cmdclass={'build_py': BuildCommand},
    entry_points={'console_scripts': ['sciunit=sciunit2.cli:main']},
    data_files=[('man/man1', ['sciunit.1.gz'])],
    package_data={'sciunit2.command.post_install': ['sciunit-completion.*'],
                  'sciunit2.command.exec_': ['sciunit']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Science/Research',
    ]
)
