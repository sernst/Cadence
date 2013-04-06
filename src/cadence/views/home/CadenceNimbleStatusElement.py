# CadenceNimbleStatusElement.py
# (C)2013
# Scott Ernst

from PySide import QtGui

from pyglass.elements.PyGlassElement import PyGlassElement

#___________________________________________________________________________________________________ CadenceNimbleStatusElement
class CadenceNimbleStatusElement(PyGlassElement):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        """Creates a new instance of CadenceNimbleStatusElement."""
        super(CadenceNimbleStatusElement, self).__init__(parent, **kwargs)

        mainLayout = self._getLayout(self, QtGui.QVBoxLayout)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ paintEvent
    def paintEvent(self, *args, **kwargs):
        """Doc..."""
        pass

#___________________________________________________________________________________________________ refresh
    def refresh(self):
        pass
