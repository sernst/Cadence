# __init__.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

from pyaid.file.FileUtils import FileUtils

#_______________________________________________________________________________
def getProjectPath(*args, **kwargs):
    return FileUtils.createPath(
        FileUtils.getDirectoryOf(__file__),
        '..', '..', *args, **kwargs)
