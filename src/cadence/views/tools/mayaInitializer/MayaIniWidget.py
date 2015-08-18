# MayaIniWidget.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.views.tools.mayaInitializer.MayaIniRemoteThread import MayaIniRemoteThread

#_______________________________________________________________________________
class MayaIniWidget(PyGlassWidget):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    RESOURCE_FOLDER_PREFIX = ['tools']

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        """Creates a new instance of MayaIniWidget."""
        super(MayaIniWidget, self).__init__(parent, **kwargs)

        self.runBtn.clicked.connect(self._handleExecute)
        self.removeBtn.clicked.connect(self._handleRemove)

        self._thread = None

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _runInitializer(self, install =True, test =False):
        self.mainWindow.showStatus(self, u'Initializing Maya', u'Running Maya Initialization')

        self._thread = MayaIniRemoteThread(self, test=test, install=install)
        self._thread.execute(self._handleInitializerComplete, self._handleThreadLog)

#_______________________________________________________________________________
    def _deactivateWidgetDisplayImpl(self, **kwargs):
        self.mainWindow.getWidgetFromID('home').refreshMayaStatus()

#===============================================================================
#                                                                                 H A N D L E R S

#_______________________________________________________________________________
    def _handleExecute(self):
        self._runInitializer(install=True, test=self.testChk.isChecked())

#_______________________________________________________________________________
    def _handleRemove(self):
        self._runInitializer(install=False, test=self.testChk.isChecked())

#_______________________________________________________________________________
    def _handleInitializerComplete(self, event):
        self.mainWindow.showStatusDone(self)
        self.refreshGui()
        self._thread = None

#_______________________________________________________________________________
    def _handleThreadLog(self, event):
        self.mainWindow.appendStatus(self, event.get('message'))
