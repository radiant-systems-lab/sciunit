.. image:: https://github.com/depaul-dice/sciunit/actions/workflows/ubuntu.yaml/badge.svg
    :target: https://github.com/depaul-dice/sciunit/actions/workflows/ubuntu.yaml
.. image:: https://img.shields.io/pypi/v/sciunit2
   :alt: PyPI
   :target: https://pypi.org/project/sciunit2/
 
Sciunit
----------

**sciunit** is a command-line tool that answers the call for a
reusable research object that containerizes and stores applications
simply and efficiently, facilitates sharing and collaboration, and
eases the task of executing, understanding, and building on shared
work.

Installing
=============

This section introduces the binary distributions of sciunit.

Requires: pip>=8.1.1, glibc>=2.17, python2.7 with headers and compiler

Platform: amd64-pc-linux-gnu

Ensure that *~/.local/bin* is in your ``PATH`` environment variable,
and then, run

::

    pip2 install --user sciunit2

Add ``--upgrade`` to the command line arguments to upgrade an existing
sciunit installation.

*[ Note*
Attempt to install sciunit with "pip install sciunit" will get you something
else; our PyPI project is registered as "sciunit2".
*--end note ]*

Verify the installation with

::

    sciunit --version

In the following per-distro instructions, if you see a command-line
in the form of

::

    export PATH=~/.local/bin:$PATH

, it merely means that you will need the aforementioned binary path
in ``PATH`` before proceeding; normally you should adjust it according
to your login shell and write it to a shell configuration such as
*~/.profile*.

Ubuntu 16.04
~~~~~~~~~~~~~
::

    sudo apt update
    sudo apt install python-dev python-pip
    pip2 install --user sciunit2

Ubuntu 14.04
~~~~~~~~~~~~~
::

    sudo apt update
    sudo apt install python-dev python-pip
    pip2 install --user -U pip
    export PATH=~/.local/bin:$PATH
    pip2 install --user sciunit2


Arch Linux
~~~~~~~~~~~~~
::

    sudo pacman -S python2-pip
    export PATH=~/.local/bin:$PATH
    pip2 install --user sciunit2

Fedora 26
~~~~~~~~~~~~~
::

    sudo dnf install python2-pip python2-devel gcc redhat-rpm-config
    pip2 install --user sciunit2

CentOS 7
~~~~~~~~~~~~~
::

    sudo yum install -y epel-release
    sudo yum install python2-pip python-devel gcc
    pip2 install --user sciunit2

RHEL 7
~~~~~~~~~~~~~
::

    sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    sudo yum install python2-pip python-devel gcc
    pip2 install --user sciunit2

Debian 9
~~~~~~~~~~~~~
::

    sudo apt update
    sudo apt install python-dev python-pip
    export PATH=~/.local/bin:$PATH
    pip2 install --user sciunit2

Debian 8
~~~~~~~~~~~~~
::

    sudo apt update
    sudo apt install python-dev python-pip
    pip2 install --user -U pip
    export PATH=~/.local/bin:$PATH
    pip2 install --user sciunit2

OpenSUSE 42
~~~~~~~~~~~~~

Note that OpenSUSE defaults user-binary path to *~/bin* rather than
*~/.local/bin*, so you may want to symlink one to the other.

::

    sudo zypper install python-pip python-devel gcc
    pip2 install --user -U pip
    export PATH=~/.local/bin:$PATH
    pip2 install --user sciunit2

Build from Source
~~~~~~~~~~~~~~~~~~~

Instructions for `custom build
<https://bitbucket.org/geotrust/sciunit2/src/master/docs/build.md>`_
of sciunit2 is available in our Bitbucket project repository.  You may
want to check it out if you are running on a system that is not
supported by the binary distribution.

Post-install
=============

Execute

::

    sciunit post-install

as a normal user to add command-line completion support for
**sciunit** to your login shell.  When running this or any other
sciunit command, if your environment is not listed in the
`Installing`_ section, or you missed some prerequisites before
issuing ``pip``, you may observe the following error:

::

    ImportError: No module named _bsddb

Fortunately, there are more than one ways to fulfill this dependency.
Try to find and install a package often named "python-bsddb" or
"python-bsddb3" with your system package manager.  In Anaconda,
you will need a port called "bsddb."

To make the command-line completion work, if you are a **bash** users,
make sure that you have the "bash-completion" package installed on your
system.  If you are a **tcsh** user, make sure that you have
``source ~/.complete`` in *~/.cshrc* or *~/.tcshrc* as suggested by
the stock `completion script
<https://github.com/tcsh-org/tcsh/blob/master/complete.tcsh>`_.

Using
===========

Checkout our `tutorial <https://sciunit.run/docs/>`_ and manpage.
The manpage is available as

::

    man sciunit

after a successful installation.

Sciunit acknowledges support from the National Science Foundation,
Bloomberg Foundation, and DePaul University.
