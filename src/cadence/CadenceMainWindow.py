# CadenceMainWindow.py
# (C)2013
# Scott Ernst

from PySide import QtGui

from pyglass.windows.PyGlassWindow import PyGlassWindow

# AS NEEDED: from cadence.models import tracks
from cadence.views.home.CadenceHomeWidget import CadenceHomeWidget
from cadence.views.tools.CadenceToolViewerWidget import CadenceToolViewerWidget

#___________________________________________________________________________________________________ CadenceMainWindow
class CadenceMainWindow(PyGlassWindow):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        PyGlassWindow.__init__(
            self,
            widgets={
                'home':CadenceHomeWidget,
                'toolViewer':CadenceToolViewerWidget },
            title='Cadence Toolset',
            **kwargs )
        self.setMinimumSize(1200,500)
        self.setContentsMargins(0, 0, 0, 0)

        widget = self._createCentralWidget()
        layout = QtGui.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)

        self.setActiveWidget('home')

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _initializeImpl
    def _initializeImpl(self, *args, **kwargs):
        # Initialize databases
        from cadence.models import tracks
        super(CadenceMainWindow, self)._initializeImpl()
