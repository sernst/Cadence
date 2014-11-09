# MayaUtils.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

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

#___________________________________________________________________________________________________ seSelection
    @classmethod
    def setSelection(cls, selection, add =False, **kwargs):
        """Modifies Maya's current selection state to the specified selection list."""
        if selection:
            cmds.select(selection, add=add, **kwargs)

