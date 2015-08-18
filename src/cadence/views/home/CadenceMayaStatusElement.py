# CadenceMayaStatusElement.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtGui
from pyglass.gui.PyGlassGuiUtils import PyGlassGuiUtils
from pyglass.elements.PyGlassElement import PyGlassElement
from pyglass.themes.ColorSchemes import ColorSchemes
from pyglass.themes.ThemeColorBundle import ThemeColorBundle

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.views.tools.mayaInitializer.MayaIniRemoteThread import MayaIniRemoteThread

#_______________________________________________________________________________
class CadenceMayaStatusElement(PyGlassElement):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    _CHECKING_LABEL = u'Checking Maya...'
    _CHECKING_INFO  = u'Trying to verify Maya installation and settings'

    _ACTIVE_LABEL = u'Maya Ready'
    _ACTIVE_INFO  = u'Maya has been initialized for use with Cadence'

    _INACTIVE_LABEL = u'Maya Not Installed'
    _INACTIVE_INFO  = u'No Maya installation was found on your computer'

    _FAILED_LABEL = u'Maya Not Initialized'
    _FAILED_INFO  = u'Maya has not been initialized for use with Cadence'

    _LABEL_STYLE  = "QLabel { font-size:16px; color:#C#; }"
    _INFO_STYLE   = "QLabel { font-size:11x; color:#C#; }"

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        """Creates a new instance of CadenceNimbleStatusElement."""
        super(CadenceMayaStatusElement, self).__init__(parent, **kwargs)
        self._colors  = None
        self._running = False
        self._status  = False

        mainLayout = self._getLayout(self, QtGui.QVBoxLayout)
        self.setContentsMargins(6, 6, 6, 6)

        self._label = QtGui.QLabel(self)
        self._label.setText(self._CHECKING_LABEL)
        mainLayout.addWidget(self._label)

        self._info = QtGui.QLabel(self)
        self._info.setText(self._CHECKING_INFO)
        mainLayout.addWidget(self._info)

        self._buttonBox, buttonLayout = self._createWidget(self, QtGui.QHBoxLayout, True)
        buttonLayout.addStretch()

        btn = QtGui.QPushButton(self._buttonBox)
        btn.setText(u'Refresh')
        btn.setEnabled(False)
        btn.clicked.connect(self._handleRetryClick)
        self._refreshBtn = btn
        buttonLayout.addWidget(btn)

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def paintEvent(self, *args, **kwargs):
        """Doc..."""
        if self._colors:
            PyGlassGuiUtils.gradientPainter(
                self, self.size(), self._colors.light.qColor, self._colors.dark.qColor)

#_______________________________________________________________________________
    def refresh(self):
        if self._running:
            return

        self._running = True
        self._colors = ThemeColorBundle(ColorSchemes.BLUE)
        self._status = False
        self._label.setText(self._CHECKING_LABEL)
        self._info.setText(self._CHECKING_INFO)
        self._refreshBtn.setEnabled(False)

        CadenceEnvironment.MAYA_IS_INITIALIZED = False

        MayaIniRemoteThread(
            self.mainWindow, False, False, check=True, verbose=False).execute(
            self._handleMayaCheckResults)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _handleRetryClick(self):
        self.refresh()

#_______________________________________________________________________________
    def _handleMayaCheckResults(self, event):
        self._running = False

        if event.target.output['success']:
            # Run an ls command looking for the time nodeName (to prevent large returns)
            self._colors = ThemeColorBundle(ColorSchemes.GREEN)
            self._status = True
            self._label.setText(self._ACTIVE_LABEL)
            self._info.setText(self._ACTIVE_INFO)
            CadenceEnvironment.MAYA_IS_INITIALIZED = True
        else:
            self._colors = ThemeColorBundle(ColorSchemes.RED)
            self._status = False
            self._label.setText(self._FAILED_LABEL)
            self._info.setText(self._FAILED_INFO)
            CadenceEnvironment.MAYA_IS_INITIALIZED = False

        self._label.setStyleSheet(self._LABEL_STYLE.replace('#C#', self._colors.strong.web))
        self._info.setStyleSheet(self._INFO_STYLE.replace('#C#', self._colors.weak.web))

        self._refreshBtn.setEnabled(not self._status)
        self._buttonBox.setVisible(not self._status)
        self.update()
