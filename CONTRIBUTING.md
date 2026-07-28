### Instructions for developers working with Sciunit on Ubuntu

1. Install Python 3.x. The latest tested and recommended version is Python 3.13.

2. Install the Git version control system:

`sudo apt update`

`sudo apt install git`

3. Download Sciunit source code, rename the project folder, and `cd` into it as follows:

`git clone https://github.com/radiant-systems-lab/sciunit.git sciunit2-python3`

`cd sciunit2-python3`

4. Install pip for Python 3:

`sudo apt-get install python3-pip`

5. Install these packages:

`pip install --upgrade pytest-metadata`

`pip install --upgrade tox`

`sudo apt install cmake`

6. Install the requirements from `test-requirements.txt` and `requirements.txt`:

`pip install -r requirements.txt`

`pip install -r test-requirements.txt`

7. Make sure you are up to date with the master branch:

`git pull origin master`

8. Run the following command from the project folder to run all tests.:

`tox`

All tests should pass. If there are any errors, follow the error messages and resolve them first.


9. At this point, you can start adding your code to Sciunit. DO NOT start working in the master branch. Make sure you checkout your own branch:

`git checkout -b new_branch_name`

10. During development, make sure to commit all changes in your branch locally, and push them to the remote repository periodically:

`git push origin master`

Note: To push the changes, you would first need to be added as a contributor.

11. After all your changes are commited, run `tox` to make sure all tests pass.

12. To test the installation in production, you can install Sciunit with your changes locally.

`pip install sciunit2-python3/`

13. After your changes are finalized in your branch, do a final code review and send a merge request with the master branch. After a successful merge, package the code and upload to PyPI. You would need the credentials for the Sciunit account on PyPI:
 
`pip install --user --upgrade twine`

`python setup.py sdist bdist_wheel`

`twine upload dist/*`


### Some notes for understanding Sciunit (for new developers):

Sciunit uses application virtualization (AV) tool provenance-to-use (PTU) built on top of Code, Data, and Environment (CDE) to containerize an application as it executes.
ptu creates a directory structure called cde-package
A tar archive of cde-package/ is sent to sciunit-dedup (formerly vvpkg) for deduplication

1. Committing a package to the deduplicated storage:
	a. take an execution directory (cde-package/) as input 
	b. convert it into a tar archive
	c. sciunit-dedup performs deduplication on the archive and stores it into blocks
2. Reconstructing an execution directory from the de-duplicated storage:
	a. extract relevant blocks from the sciunit-dedup storage.
	b. create a tar archive by concatenating the blocks from the original file entries.
	c. untar the archive to get the execution directory
3.  'create' command does the following:
	a. creates an empty dir for the project
	b. opens the project
4. 'exec' does the following:
	a. creates a sciunit.db file in the project dir. 
	b. creates cde-package dir in the sciunit folder
	c. calls commit
		At the end of exec, *.json, vvpkg.bin and vvpkg.db files have 
		been created in the project folder.
5. 'commit' does this:
	a. archives the cde-package directory and writes it to sciunit-dedup
	b. deletes the cde-package directory
	c. adds the new execution to sciunit db
6. 'repeat' does this:
	a. does ContextCheckout (see #7)
	b. reads execution commands from cde.log
	c. writes new cde.log with new arguments for the same execution commands
	d. creates a Script object from cde.log and executes it as a subprocess
7. ContextCheckout does this:
	a. removes any existing cde-package/ present
	b. checks out the given execution from the database using 'checkout' command.
	c. untar the archive obtained from checkout
	This builds cde-package directory as it was present at the time of the given execution.
