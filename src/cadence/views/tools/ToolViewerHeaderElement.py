# ToolViewerHeaderElement.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtGui

from pyglass.gui.PyGlassGuiUtils import PyGlassGuiUtils
from pyglass.elements.PyGlassElement import PyGlassElement

#_______________________________________________________________________________
class ToolViewerHeaderElement(PyGlassElement):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        """Creates a new instance of ToolViewerHeaderElement."""
        super(ToolViewerHeaderElement, self).__init__(parent, **kwargs)

        layout = self._getLayout(self, QtGui.QHBoxLayout)
        layout.setContentsMargins(6, 6, 6, 6)

        label = QtGui.QLabel(self)
        label.setText(u' ')
        label.setStyleSheet("QLabel { font-size:18px; color:#CCC; }")
        self._headerLabel = label
        layout.addWidget(label)
        layout.addStretch()

        btn = QtGui.QPushButton(self)
        btn.setText('Help')
        btn.clicked.connect(self._handleToggleHelp)
        layout.addWidget(btn)
        self._helpBtn = btn

        btn = QtGui.QPushButton(self)
        btn.setText('Close')
        btn.clicked.connect(self._handleCloseTool)
        layout.addWidget(btn)

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def toggleHelpButton(self, value):
        self._helpBtn.setEnabled(value)

#_______________________________________________________________________________
    def setLabel(self, value):
        """Doc..."""
        self._headerLabel.setText(value)

#_______________________________________________________________________________
    def paintEvent(self, *args, **kwargs):
        PyGlassGuiUtils.fillPainter(self, self.size(), QtGui.QColor.fromRgb(50, 50, 50))

#===============================================================================
#                                                                                 H A N D L E R S

#_______________________________________________________________________________
    def _handleCloseTool(self):
        self.mainWindow.setActiveWidget('home')

#_______________________________________________________________________________
    def _handleToggleHelp(self):
        self.owner.toggleHelpDisplay()
