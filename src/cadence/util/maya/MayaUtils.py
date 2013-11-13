# MayaUtils.py
# (C)2013
# Scott Ernst

import os

from pyaid.OsUtils import OsUtils
from pyaid.file.FileUtils import FileUtils

from nimble import cmds

#___________________________________________________________________________________________________ MayaUtils
class MayaUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ locateMayaEnvFiles
    @classmethod
    def locateMayaEnvFiles(cls):
        """ Finds the location of all Maya.env files located in the default location on the host
            and return them as a list. If no such env files exist, the method returns an empty
            list. """

        documents = FileUtils.cleanupPath(os.path.expanduser('~'), isDir=True)
        if not os.path.exists(documents):
            return []

        if OsUtils.isWindows():
            root = FileUtils.createPath(documents, 'maya', isDir=True)
            if not os.path.exists(root):
                return []
        elif OsUtils.isMac():
            root = FileUtils.createPath(
                documents, 'Library', 'Preferences', 'Autodesk', 'maya', isDir=True)
            if not os.path.exists(root):
                return []
        else:
            return []

        out = []
        FileUtils.walkPath(root, cls._handleFindEnvFiles, out)
        return out

#___________________________________________________________________________________________________ getSelection
    @classmethod
    def getSelection(cls, longNames =True, **kwargs):
        """Gets the list of currently selected items."""
        return cmds.ls(selection=True, long=longNames, **kwargs)

#___________________________________________________________________________________________________ getSelectedTransforms
    @classmethod
    def getSelectedTransforms(cls):
        """Gets the list of selected transforms."""
        return cls.getSelection(exactType=u'transform')

#___________________________________________________________________________________________________ seSelection
    @classmethod
    def setSelection(cls, selection, add =False, **kwargs):
        """Modifies Maya's current selection state to the specified selection list."""
        if selection:
            cmds.select(selection, add=add, **kwargs)

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleFindEnvFiles
    @classmethod
    def _handleFindEnvFiles(cls, walkData):
        for name in walkData.names:
            if name == u'Maya.env':
                walkData.data.append(FileUtils.createPath(walkData.folder, name))
