.. -*- mode: rst ; ispell-local-dictionary: "american" -*-

==========================
sciunit
==========================
-------------------------------------------------------------
deliver reproducibility in your research
-------------------------------------------------------------
:Author:    Tanu Malik <tanu@missouri.edu>
:Version:   sciunit2 0.4
:Manual section: 1
:Copyright: Copyright 2020-2021, DePaul University
:Licence:   FreeBSD License (BSD-2-Clause)

.. raw:: manpage

   .\" disable justification (adjust text to left margin only)
   .ad l


SYNOPSIS
==========

``sciunit`` [--version] [--help]

``sciunit`` <command> [<args...>]

DESCRIPTION
============

**This page might have outdated information. The most updated Sciunit documentation can be found at:**
**https://github.com/radiant-systems-lab/sciunit/wiki**

A command line utility to create, manage, and share *sciunits*.
A *sciunit* is a lightweight and portable unit that contains captured,
repeatable program executions.

OPTIONS
========

General Options
--------------------

``--version``         show program's version number and exit

``-h, --help``        show help message and exit


Commands
-----------------

``sciunit create`` <name>
          Create a new sciunit under *~/sciunit/<name>* and open it.
          If the directory already exists, exit with an error.

``sciunit open`` <name>|<token#>|<path to sciunit.zip>|<url>
          Open the sciunit under *~/sciunit/<name>* or designated by
          a *token#* obtained from ``sciunit copy``, or one in a
          zipped sciunit package which may come from a <url> by
          extracting it to a temporary directory.

``sciunit open -m`` <name>
          Rename the currently-opened sciunit to *<name>* and open it.

``sciunit exec`` <executable> [<args...>]
          Capture the execution of the given *executable* with
          the command line arguments *args*.  The newly-created
          execution is added to the
          currently-opened sciunit and assigned execution id "*eN*",
          where *N* is a monotonically-increasing decimal.
          The first execution created in a sciunit has execution id
          "*e1*".

          Note that the command line is launched using `execvp(3)`
          rather than interpreted by a shell.

``sciunit exec -i``
          Launch the current user's shell and capture the user's
          interactions with the shell.  This may involve executing
          multiple commands.  A new execution is created on exiting
          the shell.

``sciunit repeat`` <execution id>
          Repeat the execution of *execution id* from the
          currently-opened sciunit exactly as it happened earlier.

``sciunit list``
          List the existing executions in the currently-opened sciunit.

``sciunit show`` [<execution id>]
          Show detailed information about a specific execution in the
          currently-opened sciunit.

``sciunit given`` <glob> ``repeat`` <execution id> [<%|args...>]
          Repeat the execution of *execution id* with additional files
          or directories
          specified by *glob*.  The command expands *glob* into a list
          of filenames in the style of `glob(3)`, substitutes the first
          occurrence of *%*, if any, in the optional *args* for the
          ``repeat`` mini-command with those filenames, and repeats the
          execution as if those files or directories are available
          relative to its
          current working directory at capture time.

``sciunit commit``
          Commit the last repetition done by the ``repeat`` or the
          ``given`` command in the currently-opened
          sciunit as a new execution.

``sciunit rm`` <execution id>
          Remove an existing execution from the currently-opened
          sciunit.  A malformed execution id causes an error.
          Removing a nonexistent execution has no effect.

          Note: the execution is removed from the records, but its
          data remains and may be shared with other executions.

``sciunit rm`` *eN*-[*M*]
          Remove executions within a range, from *eN* to *eM*,
          inclusive.  *M* may be omitted for a range from *eN* to
          the most recent.

``sciunit sort`` <execution ids...>
          Reorder the executions in the currently-opened sciunit to
          ensure that the executions specified in the arguments
          appear consecutively in the ``sciunit list`` command.

``sciunit push`` <codename> --setup <service>
          Create an article on a research object sharing *service*
          and attach the currently-opened sciunit to the article.
          Assign different *codenames* to track multiple articles or
          multiple versions of an article created from a sciunit.
          The supported services include
          figshare_ (`fs`) and HydroShare_ (`hs`).

``sciunit push`` [<codename>]
          Update the last pushed article with the latest sciunit data
          if no argument present.  Otherwise, update the article
          referred to by *codename*.

``sciunit copy``
          Copy the currently-opened sciunit to
          `file.io <https://file.io/>`_ and obtain a token for
          remotely opening it.  The token is invalidated after being
          accessed or after one day, whichever happens first.

``sciunit copy -n``
          Archive the currently-opened sciunit to
          *~/sciunit/<name>.zip*.

SEE ALSO
=============

.. _HydroShare:

HydroShare: https://www.hydroshare.org/

.. _figshare:

figshare: https://figshare.com/
