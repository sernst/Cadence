# MayaUtils.py
# (C)2013
# Scott Ernst

from nimble import cmds

#___________________________________________________________________________________________________ MayaUtils
class MayaUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

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
