# Note: Converted

from sciunit2.util import mkdir_derivedfrom

import os
import zipfile2
from zipfile import BadZipfile
from scandir import scandir
from functools import reduce


# create a single rooted zip64 file aside the root
# ignore any subdirectories
def make(directory):
    p = os.path.normpath(directory)
    fn = p + '.zip'
    root = os.path.basename(p)
    it = scandir(directory)
    with zipfile2.ZipFile(fn, 'w', zipfile2.ZIP_DEFLATED, low_level=True) as f:
        for entry in it:
            if entry.is_file():  # hereby skips "cde-package"
                f.write(entry.path, os.path.join(root, entry.name))
    return fn


# extract a single rooted zip file
# avoid overwriting by randomizing the directory postfix
# root_constraint is the function '_is_path_component'
# root_transform is the function 'location_for'
def extract(fn, root_constraint, root_transform):
    with zipfile2.ZipFile(fn) as f:
        ls = f.namelist()  # list of file names in the archive
        if not ls:
            raise BadZipfile('empty ZIP file')
        # p contains all unique dirs referenced in the zip file
        # the map gets names of all directories in the zip file
        p = reduce(lambda x, y: x if x == y else '', map(_get_root, ls))
        if not root_constraint(p):
            raise BadZipfile('suspicious ZIP source')
        np = mkdir_derivedfrom(root_transform(p), '__')
        for name in ls:
            f.extract_to(name, os.path.relpath(name, p), path=np,
                         preserve_permissions=zipfile2.PERMS_PRESERVE_ALL)
        return np


# get the first directory-like component from a zip path
def _get_root(p):
    ls = p.split('/', 1)
    if len(ls) == 1:
        return ''
    else:
        return ls[0]
