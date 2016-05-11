# CadenceNimbleStatusElement.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import nimble
from PySide import QtCore
from PySide import QtGui
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager
from pyglass.gui.PyGlassGuiUtils import PyGlassGuiUtils
from pyglass.elements.PyGlassElement import PyGlassElement
from pyglass.themes.ColorSchemes import ColorSchemes
from pyglass.themes.ThemeColorBundle import ThemeColorBundle

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enums.UserConfigEnum import UserConfigEnum
from cadence.mayan.trackway import InitializeTrackwayScene


#_______________________________________________________________________________
class CadenceNimbleStatusElement(PyGlassElement):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    _ACTIVE_LABEL = u'Nimble Connected'
    _ACTIVE_INFO  = u'An active connection exists to a Maya Nimble server'

    _INACTIVE_LABEL = u'Nimble Disabled'
    _INACTIVE_INFO  = u'Nimble will remain disabled until you initiate a retry'

    _FAILED_LABEL = u'Nimble Disconnected'
    _FAILED_INFO  = u'Unable to connect to a Maya Nimble server instance'

    _LABEL_STYLE  = "QLabel { font-size:16px; color:#C#; }"
    _INFO_STYLE   = "QLabel { font-size:11x; color:#C#; }"

#_______________________________________________________________________________
    def __init__(self, parent, enabled =False, **kwargs):
        """Creates a new instance of CadenceNimbleStatusElement."""
        super(CadenceNimbleStatusElement, self).__init__(parent, **kwargs)
        self._colors      = None
        self._status      = False
        self._activeCheck = False
        self._canceled    = False
        self.disabled     = not enabled

        mainLayout = self._getLayout(self, QtGui.QVBoxLayout)
        self.setContentsMargins(6, 6, 6, 6)

        self._label = QtGui.QLabel(self)
        self._label.setText(u'Nimble Connecting...')
        mainLayout.addWidget(self._label)

        self._info = QtGui.QLabel(self)
        self._info.setText(u'Trying to establish a connection to a Maya Nimble server')
        mainLayout.addWidget(self._info)

        self._buttonBox, buttonLayout = self._createWidget(self, QtGui.QHBoxLayout, True)
        buttonLayout.addStretch()

        btn = QtGui.QPushButton(self._buttonBox)
        btn.setText(u'Connect')
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self._handleRetryClick)
        buttonLayout.addWidget(btn)
        self._runBtn = btn

        btn = QtGui.QPushButton(self._buttonBox)
        btn.setText(u'Cancel')
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self._handleCancelClick)
        buttonLayout.addWidget(btn)
        self._cancelBtn = btn

        btn = QtGui.QPushButton(self._buttonBox)
        btn.setText(u'Initialize Scene')
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self._handleInitializeSceneClick)
        btn.setVisible(False)
        buttonLayout.addWidget(btn)
        self._iniBtn = btn

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
        if self._activeCheck or self._canceled:
            return
        self._activeCheck = True

        if self.disabled:
            self._colors = ThemeColorBundle(ColorSchemes.GREY)
            self._status = False
            self._label.setText(self._INACTIVE_LABEL)
            self._info.setText(self._INACTIVE_INFO)
            CadenceEnvironment.NIMBLE_IS_ACTIVE = False
        else:
            try:
                # Run an ls command looking for the time nodeName (to prevent large returns)
                nimble.cmds.ls(exactType='time')

                self._colors = ThemeColorBundle(ColorSchemes.GREEN)
                self._status = True
                self._label.setText(self._ACTIVE_LABEL)
                self._info.setText(self._ACTIVE_INFO)
                CadenceEnvironment.NIMBLE_IS_ACTIVE = True
            except Exception as err:
                print('FAILED: Nimble connection attempt', err)
                self._colors = ThemeColorBundle(ColorSchemes.RED)
                self._status = False
                self._label.setText(self._FAILED_LABEL)
                self._info.setText(self._FAILED_INFO)
                CadenceEnvironment.NIMBLE_IS_ACTIVE = False
                self._runBtn.setText(u'Retry')

        self._label.setStyleSheet(self._LABEL_STYLE.replace('#C#', self._colors.strong.web))
        self._info.setStyleSheet(self._INFO_STYLE.replace('#C#', self._colors.weak.web))

        self._runBtn.setVisible(not self._status)
        self._cancelBtn.setVisible(not self._status)
        self._iniBtn.setVisible(self._status)

        self.update()

        if not self._status and not self.disabled:
            # noinspection PyCallByClass,PyTypeChecker
            QtCore.QTimer.singleShot(10000, self._handleTimer)
        self._activeCheck = False

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _handleTimer(self):
        if self._canceled:
            return

        if not self.isOnDisplay:
            # noinspection PyCallByClass,PyTypeChecker
            QtCore.QTimer.singleShot(20000, self._handleTimer)
        else:
            self.refresh()

#_______________________________________________________________________________
    def _handleRetryClick(self):
        self.mainWindow.appConfig.set(UserConfigEnum.NIMBLE_TEST_STATUS, True)

        self.disabled = False
        self.refresh()

#_______________________________________________________________________________
    def _handleCancelClick(self):
        if self.disabled:
            return

        self.mainWindow.appConfig.set(UserConfigEnum.NIMBLE_TEST_STATUS, False)

        self.disabled = True
        self.refresh()

#_______________________________________________________________________________
    def _handleInitializeSceneClick(self):
        conn   = nimble.getConnection()
        result = conn.runPythonModule(InitializeTrackwayScene)
        if not result.success:
            header = u'Failed'
            message = u'Unable to initialize your Maya scene'
            PyGlassBasicDialogManager.openOk(
                self.mainWindow,
                header,
                message,
                u'Initialize Scene')
        self._iniBtn.setText(u'Reinitialize')

